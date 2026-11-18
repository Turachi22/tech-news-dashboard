"""فراخوانی Gemini: استریم، جست‌وجوی وب، لینک منابع و چرخش خودکار بین مدل و کلید."""
import re
import time

import streamlit as st
from google import genai
from google.genai import types

from core.ai.config import (DAILY_REQUEST_LIMIT, MAX_ATTEMPTS_PER_CLICK, MIN_SECONDS_BETWEEN_CALLS,
                            THINKING_BUDGET)
from core.ai.gemini_models import (_block, _blocked, _brief, _candidates, _code, _count_request, _get_keys,
                                   _is_blocked, _is_quota, _reasons, usage_today)
from core.helpers import fa


def _link_citations(text, ext_sources):
    """ارجاع‌های [3] یا [2][5] یا [۳] را به لینک واقعی همان منبع تبدیل می‌کند؛ شمارهٔ منابع استفاده‌شده را هم برمی‌گرداند."""
    used = []

    def sub(m):
        out = []
        for tok in re.findall(r"\d+", m.group(1)):
            n = int(tok)
            if 1 <= n <= len(ext_sources):
                if n not in used:
                    used.append(n)
                out.append(f"[{n}]({ext_sources[n - 1][0]})")
        return " ".join(out) if out else m.group(0)

    text = re.sub(r"\[(\d+(?:\s*[,،]\s*\d+)*)\]", sub, text)
    return text, sorted(used)


def _stream(client, model_name, prompt, box, use_search=True, ext_sources=None):
    _count_request()
    kwargs = dict(
        temperature=0.4,
        tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else None,
    )
    if THINKING_BUDGET is not None and "2.5" in model_name and "pro" not in model_name:
        try:
            kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
        except Exception:  # noqa: BLE001  (نسخهٔ قدیمی کتابخانه)
            pass
    cfg = types.GenerateContentConfig(**kwargs)
    text, sources = "", {}
    for chunk in client.models.generate_content_stream(model=model_name, contents=prompt, config=cfg):
        text += chunk.text or ""
        try:
            for gc in chunk.candidates[0].grounding_metadata.grounding_chunks or []:
                if gc.web and gc.web.uri:
                    sources.setdefault(gc.web.uri, gc.web.title or gc.web.uri)
        except (AttributeError, IndexError, TypeError):
            pass
        box.markdown(text + " ▌")
    if ext_sources is not None:
        if ext_sources:
            text, used = _link_citations(text, ext_sources)
            show = used or list(range(1, len(ext_sources) + 1))
            head = ("**منابع (فقط مواردی که در متن به آن‌ها ارجاع شده؛ لینک‌های واقعی از جست‌وجوی Groq):**"
                    if used else "**منابع (لینک‌های واقعی از جست‌وجوی Groq):**")
            text += "\n\n---\n" + head + "\n" + "\n".join(
                f"{n}. [{ext_sources[n - 1][1]}]({ext_sources[n - 1][0]})" for n in show)
        else:
            text += "\n\n---\n⚠️ جست‌وجو لینکی برنگرداند؛ اطلاعات را پیش از انتشار راستی‌آزمایی کنید."
    elif sources:
        text += "\n\n---\n**منابع (لینک‌های واقعی از جست‌وجوی گوگل):**\n" + "\n".join(
            f"{i}. [{title}]({uri})" for i, (uri, title) in enumerate(sources.items(), 1))
    elif use_search:
        text += "\n\n---\n⚠️ این بار جست‌وجو لینکی برنگرداند؛ اطلاعات را پیش از انتشار راستی‌آزمایی کنید."
    else:
        text += "\n\n---\n⚠️ این پاسخ بدون جست‌وجوی وب تولید شده و لینک منبع ندارد؛ پیش از انتشار حتماً راستی‌آزمایی کنید."
    box.markdown(text)
    return text


class SearchUnavailable(Exception):
    """جستجوی وب در دسترس نیست و کار فعلی بدون جستجو معنی ندارد (مثل پیشنهاد خبر تازه)."""


def _search_blocked(kid):
    return _blocked().get(f"{kid}:search", 0) > time.time()


def _run(client, name, prompt, box, kid="", need_search=False, ext_sources=None):
    """با جست‌وجو اجرا می‌کند. اگر ۴۲۹ یا خطای جست‌وجو آمد، همان مدل را بدون جست‌وجو امتحان می‌کند
    (سهمیهٔ جست‌وجوی گوگل جدا و کوچک است و بین همهٔ مدل‌های یک کلید مشترک). اگر بدون جست‌وجو جواب داد،
    جست‌وجو برای همان کلید ۲ ساعت کنار می‌رود تا درخواست‌های بعدی بی‌جهت خطا نخورند."""
    if ext_sources is not None:   # منابع را Groq آورده؛ Gemini فقط می‌نویسد (بدون جست‌وجوی گوگل)
        return _stream(client, name, prompt, box, use_search=False, ext_sources=ext_sources)
    skey = f"{kid}:search"
    if "gemma" in name or _blocked().get(skey, 0) > time.time():
        if need_search:
            raise SearchUnavailable()
        return _stream(client, name, prompt, box, use_search=False)
    try:
        return _stream(client, name, prompt, box)
    except Exception as exc:  # noqa: BLE001
        low = str(exc).lower()
        if "limit: 0" in low and not any(w in low for w in ("grounding", "search")):
            raise  # خود مدل در پلن رایگان نیست؛ امتحان بدون جست‌وجو بی‌فایده است
        if _is_quota(low) or any(w in low for w in ("google_search", "grounding", "googlesearch", "search")):
            if need_search:
                _blocked()[skey] = time.time() + 7200
                raise SearchUnavailable() from exc
            text = _stream(client, name, prompt, box, use_search=False)  # اگر این هم خطا داد، بالا می‌رود
            _blocked()[skey] = time.time() + 7200
            st.warning("سهمیهٔ جست‌وجوی وب (برای لینک منبع) روی این کلید تمام یا در دسترس نبود؛ "
                       "پاسخ بدون لینک تولید شد. برای لینک واقعی از «بدون API» استفاده کنید "
                       "یا بعداً دوباره امتحان کنید.")
            return text
        raise


def _retryable(exc):
    low = str(exc).lower()
    return (_is_quota(low) or _code(low, "404") or _code(low, "403") or _code(low, "503")
            or "unavailable" in low or "high demand" in low
            or any(w in low for w in ("no longer available", "not found", "not supported",
                                      "api_key_invalid", "api key not valid", "permission_denied")))


def ask_ai(prompt, box=None, need_search=False, ext_sources=None, quiet=False):
    """جدیدترین مدل رایگان را با کلیدها به‌نوبت امتحان می‌کند؛ بعد سراغ مدل قدیمی‌تر می‌رود."""
    ss = st.session_state
    keys = _get_keys()
    if not keys:
        st.error("لطفاً حداقل یک کلید Gemini وارد کنید (منوی کناری یا Secrets).")
        return None
    if time.time() - ss.get("_last_ai_call", 0) < MIN_SECONDS_BETWEEN_CALLS:
        st.warning(f"لطفاً {fa(MIN_SECONDS_BETWEEN_CALLS)} ثانیه بین دو درخواست صبر کنید.")
        return None
    if usage_today() >= DAILY_REQUEST_LIMIT:
        st.error(f"سقف {fa(DAILY_REQUEST_LIMIT)} درخواست در روز پر شده است (برای حفظ سهمیهٔ رایگان). "
                 "اگر لازم است، DAILY_REQUEST_LIMIT را در core/ai.py بالا ببرید.")
        return None
    if need_search and ext_sources is None and all(_search_blocked(k[-4:]) for k in keys):
        if not quiet:
            st.warning("جستجوی وب (سهمیهٔ جستجوی گوگل) فعلاً در دسترس نیست. پیشنهاد خبر تازه بدون جستجو ساخته نمی‌شود، "
                       "چون مدل ممکن است خبر ساختگی بدهد. بعداً دوباره امتحان کنید یا خبر را دستی اضافه کنید.")
        return None
    ss["_last_ai_call"] = time.time()
    box = box if box is not None else st.empty()

    all_models, list_err = [], None
    for k in keys:
        try:
            all_models = _candidates(k)
            break
        except Exception as exc:  # noqa: BLE001
            list_err = exc
    if not all_models:
        st.error(f"دریافت فهرست مدل‌ها ناموفق بود (کلیدها را بررسی کنید): {str(list_err)[:300]}")
        return None

    skipped, last_err, tries, search_fail = [], None, 0, False
    status = st.status("در حال جست‌وجو و تحقیق...", expanded=False)
    for name in all_models:
        if tries >= MAX_ATTEMPTS_PER_CLICK:
            break
        short = name.replace("models/", "")
        for idx, key in enumerate(keys):
            kid = key[-4:]
            if _is_blocked(kid, name):
                continue
            if tries >= MAX_ATTEMPTS_PER_CLICK:
                break
            tries += 1
            status.update(label=f"در حال جست‌وجو و تحقیق با «{short}» (کلید {fa(idx + 1)})...", state="running")
            try:
                try:
                    text = _run(genai.Client(api_key=key), name, prompt, box, kid, need_search, ext_sources)
                except SearchUnavailable:
                    raise
                except Exception as exc503:  # noqa: BLE001
                    low503 = str(exc503).lower()
                    if not (_code(low503, "503") or "unavailable" in low503 or "high demand" in low503):
                        raise
                    status.update(label="سرور گوگل شلوغ است؛ چند ثانیه بعد دوباره امتحان می‌شود...", state="running")
                    time.sleep(5)   # شلوغی ۵۰۳ معمولاً موقتی است؛ یک بار با همان مدل دوباره
                    text = _run(genai.Client(api_key=key), name, prompt, box, kid, need_search, ext_sources)
            except SearchUnavailable:
                search_fail = True
                continue
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                if _retryable(exc):
                    _block(kid, name, exc)
                    skipped.append(f"{short} (کلید {fa(idx + 1)})")
                    continue
                status.update(label="خطا در ارتباط با Gemini", state="error")
                st.error(f"خطا در ارتباط با Gemini: {_brief(exc)}")
                return None
            if not text.strip():
                skipped.append(f"{short} (کلید {fa(idx + 1)})")
                continue
            ss["active_model"] = f"{short} · کلید {fa(idx + 1)}"
            status.update(label=f"تحقیق کامل شد · {short} · کلید {fa(idx + 1)}", state="complete")
            if skipped:
                st.info(f"از {'، '.join(skipped)} عبور شد؛ پاسخ با «{short}» و کلید {fa(idx + 1)} آمد.")
            return text

    if search_fail and not skipped:
        if quiet:
            status.update(label="جستجوی گوگل در دسترس نیست؛ روش جایگزین...", state="complete")
        else:
            status.update(label="جستجوی وب در دسترس نیست", state="error")
            st.warning("جستجوی وب (سهمیهٔ جستجوی گوگل) در دسترس نبود. پیشنهاد خبر تازه بدون جستجو ساخته نمی‌شود، "
                       "چون مدل ممکن است خبر ساختگی بدهد. بعداً دوباره امتحان کنید یا خبر را دستی اضافه کنید.")
        return None
    if not skipped:  # همهٔ ترکیب‌ها از قبل کنار گذاشته شده بودند
        status.update(label="همهٔ مدل‌ها فعلاً در انتظار سهمیه‌اند", state="error")
        now = time.time()
        waits = [t - now for kid_name, t in _blocked().items() if t > now]
        mins = max(round(min(waits) / 60), 1) if waits else 1
        st.error("همهٔ ترکیب‌های مدل و کلید فعلاً کنار گذاشته شده‌اند. "
                 f"نزدیک‌ترین ترکیب حدود {fa(mins)} دقیقهٔ دیگر آزاد می‌شود.")
        with st.expander("جزئیات (دلیل کنار رفتن هر مدل)"):
            for k, why in list(_reasons().items())[-8:]:
                st.code(f"{k}\n{why}", language=None)
        return None
    status.update(label="هیچ مدلی پاسخ نداد", state="error")
    st.error("هیچ ترکیبی پاسخ نداد. بخش «تنظیمات ← تست کلیدها و مدل‌ها» دلیل دقیق هر مدل را نشان می‌دهد.")
    with st.expander("جزئیات (دلیل کنار رفتن هر مدل)"):
        for k, why in list(_reasons().items())[-12:]:
            st.code(f"{k}\n{why}", language=None)
    return None
