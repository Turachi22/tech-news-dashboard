"""اتصال به Gemini: چرخش خودکار بین مدل‌ها و کلیدها، جست‌وجوی وب، لینک منابع، تشخیص خطا."""
import datetime as dt
import re
import time
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types
import streamlit as st

from core import groq_client
from core.groq_client import GroqError
from core.helpers import fa

# ---------------------------------------------------------------------------
# تنظیمات مدل‌ها — فقط همین بخش را برای عوض‌کردن مدل‌ها ویرایش کنید
# ---------------------------------------------------------------------------
# مدل‌های مجاز (رایگان) به ترتیب اولویت. برنامه اول مدل اول را امتحان می‌کند؛
# اگر سهمیه‌اش تمام شد یا در دسترس نبود، مدل بعدی را.
# فقط این سه مدل استفاده می‌شوند (به ترتیب اولویت). lite کم‌مصرف‌ترین است و اول می‌آید.
PREFERRED_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
]
# False = فقط سه مدل بالا؛ هیچ مدل دیگری امتحان نمی‌شود.
ALLOW_FALLBACK = False
# تفکر داخلی مدل‌های ۲٫۵ (flash و flash-lite): 0 = خاموش (سریع‌تر و مصرف توکن کم‌تر)،
# None = پیش‌فرض گوگل (دقیق‌تر ولی کندتر). مدل 2.5-pro و نسخه‌های 2.0 تحت‌تأثیر نیستند.
THINKING_BUDGET = 0

# اولویت جست‌وجو برای «بررسی خبر» و «پیشنهاد روزانه»:
#   "gemini" = اول جست‌وجوی خود Gemini (گوگل)؛ اگر سهمیهٔ جست‌وجویش تمام بود، خودکار Groq.
#   "groq"   = اول Groq (جست‌وجو) و Gemini فقط برای نوشتن؛ اگر Groq نبود، Gemini با جست‌وجوی خودش.
# (دکمهٔ «بررسی عمیق نظریه‌های توطئه» همیشه اول با Groq کار می‌کند.)
SEARCH_PRIORITY = "gemini"

# --- محافظ مصرف (برای جلوگیری از هدر رفتن سهمیهٔ رایگان) ---
MAX_ATTEMPTS_PER_CLICK = 8      # حداکثر تعداد تلاش (ترکیب مدل × کلید) برای یک کلیک
MIN_SECONDS_BETWEEN_CALLS = 8   # فاصلهٔ حداقل بین دو درخواست پشت‌سرهم
DAILY_REQUEST_LIMIT = 60        # سقف نرم درخواست در هر روز (بر اساس ساعت سهمیهٔ گوگل)

RESEARCH_RULES = (
    "تو دستیار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و پاسخ را به زبان فارسی، "
    "کامل، دقیق و با جزئیات بنویس (محدودیتی برای طول نیست). اعداد، تاریخ‌ها، نام افراد و شرکت‌ها را بیاور. "
    "هر ادعای مهم را با نام منبع همراه کن. هرگز خودت لینک نساز؛ لینک منابع واقعی بعد از متن "
    "به‌صورت خودکار اضافه می‌شود. اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)
NEWS_RULES = (
    "تو ویراستار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و فقط مهم‌ترین و ضروری‌ترین "
    "اطلاعات را به فارسی روان و بدون غلط املایی بنویس. اعداد، تاریخ‌ها و نام‌ها را بیاور و هر ادعای مهم را با "
    "نام منبعش همراه کن. هرگز خودت لینک نساز؛ لینک منابع بعد از متن خودکار اضافه می‌شود. "
    "اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)
NEWS_STRUCTURE = (
    "قالب پاسخ (دقیقاً با همین عنوان‌ها و به‌صورت مارک‌داون؛ فقط مهم‌ترین و ضروری‌ترین اطلاعات؛ بدون مقدمه، "
    "بدون جملهٔ تکراری و بدون هیچ توضیحی دربارهٔ خودِ گزارش):\n"
    "## ۱) خلاصهٔ ساده\n"
    "۸ تا ۱۲ جمله برای مخاطب عمومی (سطح کلاس ششم)، در این ترتیب: اول ماجرا چیست و چه اتفاقی افتاد؛ بعد چرا مهم است "
    "و چه تأثیری روی زندگی آدم‌ها دارد؛ هر اصطلاح فنی را همان‌جا با یک جملهٔ ساده توضیح بده؛ و در پایان یک مثال "
    "ملموس از زندگی روزمره یا یک تشبیه ساده بیاور که مفهوم اصلی خبر را قابل‌فهم کند، با برچسب «**مثال:**» "
    "(مثال فقط برای فهم است و نباید ادعای واقعیِ تازه‌ای باشد).\n"
    "## ۲) حقایق و آمار کلیدی\nحداکثر ۶ نقطه (• ...)؛ هر کدام یک خط شامل عدد/تاریخ/نام و ارجاع به منبع.\n"
    "## ۳) پیشینه\nحداکثر ۳ نقطه.\n"
    "## ۴) محدودیت‌ها و میزان اطمینان\nحداکثر ۴ نقطه؛ آخرین نقطه: اطمینان کلی (زیاد/متوسط/کم) با یک دلیل.\n"
    "## ۵) زاویه‌های پیشنهادی برای ویدیو\n۳ زاویه، هر کدام یک خط.\n"
    "## ۶) نظریه‌ها و شایعات توطئه‌آمیز\n"
    "این بخش برای من مهم است و باید دقیق‌تر و مفصل‌تر از بقیه باشد. برای هر ادعا (حداکثر ۴ ادعا) دقیقاً این قالب:\n"
    "### ادعا: (یک جمله)\n"
    "- **چه کسی یا کدام منبع:** نام کامل، سمت یا رسانه، و بستر (توییتر/X، مصاحبه، مقاله، پادکست، انجمن…)\n"
    "- **دقیقاً چه گفته:** نقل‌قول کوتاه یا خلاصهٔ نزدیک به متن، همراه تاریخ اگر هست\n"
    "- **مستندات له و علیه:** چه چیزی آن را تقویت می‌کند و چه چیزی رد می‌کند\n"
    "- **نظر منابع معتبر یا راستی‌آزمایان:** (یا «موردی یافت نشد»)\n"
    "- **برچسب:** ادعای اثبات‌نشده\n"
    "اگر موردی در منابع نبود فقط بنویس «در منابع بررسی‌شده موردی یافت نشد»؛ هیچ ادعا، گوینده یا نقل‌قولی نساز.\n"
    "خبر: {title} — {desc}"
)
NEWS_PROMPT = NEWS_RULES + NEWS_STRUCTURE
DEEP_PROMPT = RESEARCH_RULES + (
    "برای یک مینی‌مستند تکنولوژی دربارهٔ موضوع زیر اطلاعات پس‌زمینه، تاریخچه، حقایق کلیدی، "
    "نکته‌های کمتر شناخته‌شده و چند زاویهٔ روایی جذاب ارائه بده.\nموضوع: {title}"
)
FOLLOWUP_RULES = RESEARCH_RULES + (
    "این یک پرسش تکمیلی دربارهٔ تحقیقی است که قبلاً انجام شده. فقط به سؤال جدید پاسخ بده و اطلاعات تازه، "
    "دقیق و مستند بیاور؛ مطالب نسخه‌های قبلی را تکرار نکن، مگر برای تصحیح یک اشتباه.\n\n"
)


def build_followup_prompt(item, question, max_chars=14000):
    """پرسش جدید را همراه خلاصهٔ نسخه‌های قبلی (بدون بخش منابع) برای مدل آماده می‌کند."""
    parts, used = [], 0
    for v in reversed(item.get("research", [])):
        body = v["text"].split("\n\n---\n")[0]
        block = f"[نسخه {v['v']}" + (f" — سؤال: {v['q']}" if v.get("q") else "") + f"]\n{body}"
        if used + len(block) > max_chars:
            break
        parts.insert(0, block)
        used += len(block)
    return (FOLLOWUP_RULES + f"خبر: {item['title']} — {item['desc']}\n\n"
            "تحقیق‌ها و پرسش‌های قبلی:\n" + "\n\n".join(parts)
            + f"\n\nسؤال یا درخواست جدید: {question}")


@st.cache_resource
def _usage():
    return {"day": "", "count": 0}


def _today_pt():
    return dt.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")


def usage_today():
    u = _usage()
    if u["day"] != _today_pt():
        u["day"], u["count"] = _today_pt(), 0
    return u["count"]


def _count_request():
    usage_today()
    _usage()["count"] += 1


@st.cache_resource
def _blocked():
    """مدل‌هایی که موقتاً (به‌خاطر سهمیه) کنار گذاشته شده‌اند: نام مدل -> زمان آزاد شدن."""
    return {}


@st.cache_data(ttl=3600, show_spinner=False)
def _list_models(api_key):
    client = genai.Client(api_key=api_key)
    return [m.name for m in client.models.list()
            if "generateContent" in (getattr(m, "supported_actions", None) or [])]


def _version(name):
    m = re.search(r"gemini-(\d+(?:\.\d+)?)", name)
    return float(m.group(1)) if m else 0.0


def _discover(api_key):
    """مدل‌های flash متنی حساب شما، از جدیدترین نسخه به قدیمی‌ترین (فقط برای ALLOW_FALLBACK)."""
    skip = ("image", "tts", "live", "embedding", "audio", "exp", "vision", "robotics",
            "omni", "computer", "native", "pro")
    flash = [n.replace("models/", "") for n in _list_models(api_key)
             if ("flash" in n or "gemma" in n) and not any(x in n for x in skip)]
    flash.sort(key=lambda n: ("gemma" in n, _version(n) < 3, "latest" in n, -_version(n), "lite" in n, "preview" in n, n))
    return flash


def _candidates(api_key):
    """مدل‌های PREFERRED_MODELS که واقعاً در حساب شما وجود دارند (بدون صرف درخواست)؛
    اگر هیچ‌کدام نبود، یا ALLOW_FALLBACK روشن بود، مدل‌های flash دیگر هم اضافه می‌شوند."""
    models = list(PREFERRED_MODELS)
    discovered = []
    try:
        discovered = _discover(api_key)
        available = set(discovered) | {n.replace("models/", "") for n in _list_models(api_key)}
        models = [m for m in models if m in available]
    except Exception:  # noqa: BLE001  (فهرست در دسترس نبود؛ همان فهرست ترجیحی را نگه می‌داریم)
        pass
    if ALLOW_FALLBACK:
        models += [n for n in discovered if n not in models]
    return models


@st.cache_resource
def _reasons():
    return {}


def _brief(exc):
    """خلاصهٔ خطا: کد، نام سهمیه‌ای که تمام شده و سقف آن."""
    t = str(exc)
    ids = list(dict.fromkeys(re.findall(r"quotaId['\"]?: ?['\"]?([\w-]+)", t)))
    lim = list(dict.fromkeys(re.findall(r"limit: (\d+)", t)))
    out = t[:160].replace("\n", " ")
    if ids:
        out += " | " + ", ".join(ids)
    if lim:
        out += " | limit=" + ",".join(lim)
    return out


def _code(low, c):
    return re.search(rf"\b{c}\b", low) is not None


def _is_quota(low):
    return _code(low, "429") or "resource_exhausted" in low or "quota" in low


def _get_keys():
    """کلیدها را از Secrets (برای استقرار) و از کادرهای منوی کناری جمع می‌کند."""
    keys = []
    try:
        sec = st.secrets.get("GEMINI_API_KEYS") or st.secrets.get("GEMINI_API_KEY")
        if isinstance(sec, str):
            keys.append(sec)
        elif sec:
            keys.extend(sec)
    except Exception:  # noqa: BLE001  (فایل secrets وجود ندارد)
        pass
    keys += [st.session_state.get("api_key", ""), st.session_state.get("api_key2", "")]
    out = []
    for k in keys:
        k = (k or "").strip()
        if k and k not in out:
            out.append(k)
    return out


def _is_blocked(kid, name):
    b, now = _blocked(), time.time()
    return max(b.get(f"{kid}:*", 0), b.get(f"{kid}:{name}", 0)) > now


def _block(kid, name, exc):
    """بر اساس نوع خطا تعیین می‌کند این (کلید، مدل) تا چه زمانی کنار بماند."""
    low = str(exc).lower()
    _reasons()[f"{kid}:{name}"] = _brief(exc)
    if any(w in low for w in ("api_key_invalid", "api key not valid", "permission_denied")) or _code(low, "403"):
        _blocked()[f"{kid}:*"] = time.time() + 3600  # کلید نامعتبر
        return
    if "limit: 0" in low or _code(low, "404") or any(w in low for w in ("no longer available", "not found")):
        secs = 24 * 3600  # در پلن رایگان وجود ندارد
    elif "perday" in low.replace(" ", "") or "per day" in low:
        tz = ZoneInfo("America/Los_Angeles")  # سهمیهٔ روزانه نیمه‌شب وقت لس‌آنجلس ریست می‌شود
        now = dt.datetime.now(tz)
        nxt = (now + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        secs = (nxt - now).total_seconds()
    elif _code(low, "503") or "unavailable" in low or "high demand" in low:
        secs = 30  # شلوغی موقت سرور گوگل؛ زود دوباره امتحان می‌شود
    else:
        m = re.search(r"retry in ([\d.]+)s", low)
        secs = min(float(m.group(1)) if m else 60, 300) + 3  # سقف دقیقه‌ای
    _blocked()[f"{kid}:{name}"] = time.time() + secs


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
                       "پاسخ بدون لینک تولید شد. برای لینک واقعی از «✋ بدون API» استفاده کنید "
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


# ---------------------------------------------------------------------------
# مسیر ترکیبی: Groq جست‌وجو می‌کند (متن + لینک منابع) → Gemini بدون جست‌وجو به فارسی می‌نویسد
# ---------------------------------------------------------------------------
GROQ_NEWS_PROMPT = (
    "Research this technology news item using web search (search in both English and Persian).\n"
    "News item: {title} - {desc}\n\n"
    "Write concise research notes in two parts.\n"
    "PART A - FACTS (about 350 words): key facts with numbers, dates and names; technical details; background; "
    "limitations and criticism. Name the source and the publication date of every claim.\n"
    "PART B - CONSPIRACY THEORIES AND RUMORS (about 450 words; this part is important): find the specific "
    "conspiracy theories, rumors and unverified speculation about this item. For EACH one (max 4) give: "
    "(1) the claim in one sentence; (2) WHO said it: full name, role or outlet, and where (X/Twitter, interview, "
    "article, podcast, forum); (3) WHAT exactly they said: a short direct quote or a close paraphrase, and the date; "
    "(4) the evidence offered for it and the evidence against it; (5) what credible outlets or fact-checkers say "
    "about it; (6) the URL of the page where you found it. If you find none, say exactly that. "
    "Never invent a speaker, a quote or a URL."
)
GROQ_CONSPIRACY_PROMPT = (
    "Use web search (English and Persian) to dig deeper into the conspiracy theories, rumors and unverified "
    "speculation around this technology news item.\nNews item: {title} - {desc}\n\n"
    "For EACH distinct claim (max 6) give: (1) the claim in one sentence; (2) WHO said it: full name, role or "
    "outlet, and where (X/Twitter, interview, article, podcast, forum); (3) WHAT exactly they said: a short direct "
    "quote or close paraphrase, and the date; (4) the evidence offered for it and the evidence against it; "
    "(5) what credible outlets or fact-checkers say; (6) the URL of the page where you found it. "
    "Be specific; no vague statements like 'some people say'. If you find none, say exactly that. "
    "Never invent a speaker, a quote or a URL."
)
CONSPIRACY_FORMAT = (
    "قالب پاسخ (مارک‌داون؛ بدون مقدمه و بدون توضیح دربارهٔ گزارش). عنوان: ## 🕵️ نظریه‌ها و شایعات توطئه‌آمیز\n"
    "برای هر ادعا (حداکثر ۶ ادعا) دقیقاً این قالب:\n"
    "### ادعا: (یک جمله)\n"
    "- **چه کسی یا کدام منبع:** نام کامل، سمت یا رسانه، و بستر (توییتر/X، مصاحبه، مقاله، پادکست، انجمن…)\n"
    "- **دقیقاً چه گفته:** نقل‌قول کوتاه یا خلاصهٔ نزدیک به متن، همراه تاریخ اگر هست\n"
    "- **مستندات له و علیه:** چه چیزی آن را تقویت می‌کند و چه چیزی رد می‌کند\n"
    "- **نظر منابع معتبر یا راستی‌آزمایان:** (یا «موردی یافت نشد»)\n"
    "- **برچسب:** ادعای اثبات‌نشده\n"
    "در پایان یک جمع‌بندی دو خطی. اگر موردی در منابع نبود فقط بنویس «در منابع بررسی‌شده موردی یافت نشد»؛ "
    "هیچ ادعا، گوینده یا نقل‌قولی نساز.\nخبر: {title} — {desc}"
)
FROM_SOURCES_RULES = (
    "تو ویراستار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. مواد زیر را یک موتور جست‌وجو از وب جمع کرده است "
    "(هر منبع یک شماره دارد). فقط بر اساس همین مواد بنویس. هر عدد، تاریخ، نقل‌قول و ادعا باید با ارجاع شماره‌ای "
    "مثل [3] یا [2][5] همراه باشد؛ چیزی که در مواد نیست نیاور، حتی اگر خودت می‌دانی. "
    "تاریخ امروز {today} است؛ تاریخی بعد از امروز را فقط اگر صریحاً در مواد آمده باشد بیاور و کنارش بنویس «طبق منبع». "
    "فقط «مثال:» در بخش خلاصهٔ ساده می‌تواند از خودت باشد (تشبیه ساده، بدون ادعای واقعی تازه). "
    "فارسی روان و بدون غلط املایی؛ هیچ عبارت داخل کروشه جز ارجاع‌های شماره‌ای ننویس؛ لینک نساز.\n\n"
)


def _materials(text, srcs, max_text=14000, max_snippets=6000):
    """متن یافته‌ها + منابع شماره‌دار، برای دادن به Gemini (با سقف طول)."""
    parts = ["[یافته‌های جست‌وجو]\n" + text[:max_text]]
    lines, used = [], 0
    for i, (url, meta) in enumerate(srcs.items(), 1):
        line = f"[{i}] {meta['title']} — {url}\n    {meta['content'][:500]}"
        if used + len(line) > max_snippets:
            break
        lines.append(line)
        used += len(line)
    if lines:
        parts.append("[منابع شماره‌دار]\n" + "\n".join(lines))
    return "\n\n".join(parts)


def _groq_cached(prompt):
    """نتیجهٔ جست‌وجوی Groq برای یک پرامپت در همین نشست نگه داشته می‌شود؛ اگر Gemini خطا داد و دوباره
    امتحان کردید، Groq دوباره صدا زده نمی‌شود (صرفه‌جویی در سهمیه)."""
    cache = st.session_state.setdefault("_groq_cache", {})
    if prompt in cache:
        return cache[prompt]
    res = groq_client.search(prompt)
    if len(cache) >= 6:
        cache.pop(next(iter(cache)))
    cache[prompt] = res
    return res


def _show_raw(gtext, srcs):
    with st.expander("📄 یافته‌های خام جست‌وجو (انگلیسی) — چون Gemini پاسخ نداد", expanded=True):
        st.markdown(gtext)
        if srcs:
            st.markdown("**منابع:**\n" + "\n".join(
                f"{i}. [{m['title']}]({u})" for i, (u, m) in enumerate(srcs.items(), 1)))
        st.caption("دوباره بزنید؛ جست‌وجوی Groq تکرار نمی‌شود و فقط نوشتن فارسی با Gemini دوباره امتحان می‌شود.")


def _groq_note(exc):
    st.info(f"Groq در دسترس نبود ({str(exc)[:120]}). با روش جایگزین (Gemini) ادامه می‌دهیم.")


def _hybrid(groq_prompt, gemini_body, fallback_prompt, box=None, gemini_first=False):
    """Groq جست‌وجو می‌کند → Gemini (بدون جست‌وجو) از روی مواد می‌نویسد، ارجاع‌های [n] به لینک تبدیل می‌شوند.
    اگر Groq نبود یا خطا داد، fallback_prompt با Gemini (و جست‌وجوی خودش)."""
    groq_ok = groq_client.available()
    if gemini_first and groq_ok:
        # اول جست‌وجوی خود Gemini (اگر سهمیهٔ جست‌وجو برگشته باشد)؛ اگر نشد، ادامه با Groq
        out = ask_ai(fallback_prompt, box, need_search=True, quiet=True)
        if out:
            return out
        st.session_state["_last_ai_call"] = 0   # درخواست بعدی به‌خاطر فاصلهٔ حداقل رد نشود
    if groq_ok:
        ph = st.empty()
        ph.caption("🔎 در حال جست‌وجوی منابع...")
        try:
            gtext, srcs = _groq_cached(groq_prompt)
        except GroqError as exc:
            ph.empty()
            _groq_note(exc)
        else:
            ph.empty()
            prompt = (FROM_SOURCES_RULES.format(today=dt.date.today().isoformat()) + gemini_body
                      + "\n\n" + _materials(gtext, srcs))
            out = ask_ai(prompt, box, ext_sources=[(u, m["title"]) for u, m in srcs.items()])
            if out and st.session_state.get("active_model"):
                st.session_state["active_model"] += " + منابع Groq"
            if not out:
                _show_raw(gtext, srcs)
            return out
    return ask_ai(fallback_prompt, box)


def research_news(title, desc, box=None):
    """تحقیق یک خبر (قالب ۶ بخشی، کوتاه و مارک‌داون، با بخش مفصل نظریه‌های توطئه)."""
    return _hybrid(GROQ_NEWS_PROMPT.format(title=title, desc=desc),
                   NEWS_STRUCTURE.format(title=title, desc=desc),
                   NEWS_PROMPT.format(title=title, desc=desc), box,
                   gemini_first=(SEARCH_PRIORITY == "gemini"))


def research_conspiracies(title, desc, box=None):
    """بررسی عمیق‌تر فقط نظریه‌ها و شایعات توطئه‌آمیز یک خبر (با یک جست‌وجوی جداگانهٔ Groq)."""
    return _hybrid(GROQ_CONSPIRACY_PROMPT.format(title=title, desc=desc),
                   CONSPIRACY_FORMAT.format(title=title, desc=desc),
                   NEWS_RULES + CONSPIRACY_FORMAT.format(title=title, desc=desc), box)


SUGGEST_PROMPT = (
    "تو دستیار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب، فقط خبرهای تکنولوژی را پیدا کن که "
    "بین {start} و {end} (هر دو روز شامل) منتشر شده‌اند و دربارهٔ یک پیشرفت یا به‌روزرسانی جدید هستند "
    "(محصول، مدل هوش مصنوعی، پژوهش، کشف یا رویداد تازه). خبر قدیمی‌تر، تحلیل کلی، مطلب آموزشی و تبلیغ نیاور. "
    "حداکثر {n} خبر مهم‌ترِ متفاوت. فقط از منابع خبری معتبر بگیر و خودت لینک نساز.\n"
    "هر خبر را دقیقاً در یک خط و به این قالب بنویس، بدون هیچ متن اضافه:\n"
    "عنوان فارسی کوتاه | توضیح یک‌جمله‌ای فارسی | تاریخ انتشار (YYYY-MM-DD) | نام منبع\n"
    "{avoid}"
)


GROQ_SUGGEST_PROMPT = (
    "Use web search (English and Persian) to find up to {n} of the most important technology news items "
    "(new products, AI models, research, discoveries, events) that were PUBLISHED between {start} and {end} "
    "inclusive. Exclude older news, general analysis, tutorials and ads. For each item give: headline, a "
    "one-sentence summary, the exact publication date (YYYY-MM-DD) and the source name. Only include items whose "
    "publication date you can confirm from the source. Do not invent anything.\n{avoid}"
)
SUGGEST_FROM_SOURCES = (
    "از میان مواد زیر که موتور جست‌وجو از وب جمع کرده، حداکثر {n} خبر مهم‌ترِ متفاوت را انتخاب کن که تاریخ "
    "انتشارشان بین {start} و {end} (هر دو شامل) است. چیزی از خودت اضافه نکن و خبری که تاریخ انتشارش در مواد "
    "نیست نیاور. هر خبر را دقیقاً در یک خط و به این قالب بنویس، بدون هیچ متن اضافه:\n"
    "عنوان فارسی کوتاه | توضیح یک‌جمله‌ای فارسی | تاریخ انتشار (YYYY-MM-DD) | نام منبع\n{avoid}\n"
)


def suggest_news(end_date, days=3, n=5, existing=()):
    """خبرهای منتشرشده در بازهٔ [end_date - days, end_date] را پیشنهاد می‌دهد.
    اول Groq جست‌وجو می‌کند و Gemini خلاصه را به فارسی درمی‌آورد؛ اگر Groq نبود، Gemini با جست‌وجوی خودش.
    خروجی: (فهرست خبرها، متن بخش منابع). خبرِ بدون تاریخ معتبر یا خارج از بازه حذف می‌شود."""
    start = end_date - dt.timedelta(days=days)
    avoid = ("این عنوان‌ها قبلاً هستند؛ تکرارشان نکن: " + "؛ ".join(list(existing)[:15]) + "\n") if existing else ""
    box = st.empty()
    gem_prompt = SUGGEST_PROMPT.format(start=start.isoformat(), end=end_date.isoformat(), n=n, avoid=avoid)
    text, groq_done = None, False
    groq_ok = groq_client.available()
    if SEARCH_PRIORITY == "gemini":
        # اول جست‌وجوی خود Gemini (بی‌صدا اگر Groq هم هست)؛ فقط با جست‌وجوی واقعی، نه از حافظهٔ مدل
        text = ask_ai(gem_prompt, box, need_search=True, quiet=groq_ok)
        if text:
            box.empty()
            return _parse_suggestions(text, start, end_date)
        st.session_state["_last_ai_call"] = 0
    if groq_ok:
        try:
            gtext, srcs = _groq_cached(GROQ_SUGGEST_PROMPT.format(
                n=n, start=start.isoformat(), end=end_date.isoformat(), avoid=avoid))
            if not srcs:
                raise GroqError("Groq لینک منبعی برنگرداند")
            groq_done = True
            prompt = SUGGEST_FROM_SOURCES.format(n=n, start=start.isoformat(), end=end_date.isoformat(),
                                                 avoid=avoid) + _materials(gtext, srcs)
            text = ask_ai(prompt, box, ext_sources=[(u, m["title"]) for u, m in srcs.items()])
        except GroqError as exc:
            _groq_note(exc)
    if not groq_done and not text and SEARCH_PRIORITY != "gemini":
        text = ask_ai(gem_prompt, box, need_search=True)
    box.empty()
    return _parse_suggestions(text, start, end_date) if text else (None, "")


def _parse_suggestions(text, start, end_date):
    """خطوط «عنوان | توضیح | تاریخ | منبع» را می‌خواند و فقط خبرهای داخل بازهٔ تاریخ را نگه می‌دارد."""
    if not text:
        return None, ""
    body, _, sources = text.partition("\n\n---\n")
    items = []
    for line in body.splitlines():
        parts = [x.strip(" *-•\t") for x in line.split("|")]
        if len(parts) < 4:
            continue
        m = re.search(r"\d{4}-\d{2}-\d{2}", parts[2])
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(0))
        except ValueError:
            continue
        if not (start <= d <= end_date):
            continue
        items.append({"title": parts[0], "desc": parts[1], "date": d.isoformat(), "source": parts[3]})
    return items, sources


def quota_status():
    """فهرست مدل‌های منتظر سهمیه: [(کلید، مدل، ثانیهٔ باقی‌مانده، توضیح کوتاه)]؛ نزدیک‌ترین زمان آزاد شدن اول."""
    now = time.time()
    rows = []
    for k, t in _blocked().items():
        if t <= now:
            continue
        kid, _, name = k.partition(":")
        if name == "search":
            rows.append((kid, "جستجوی وب", t - now, "سهمیهٔ جستجو تمام شده؛ پاسخ‌ها بدون لینک تولید می‌شوند"))
            continue
        if name == "*":
            why = "کلید نامعتبر یا بدون دسترسی"
        else:
            r = _reasons().get(k, "").lower()
            if "limit=0" in r or "not found" in r or "404" in r:
                why = "در پلن رایگان این کلید در دسترس نیست"
            elif "perday" in r.replace(" ", "") or "per day" in r:
                why = "سهمیهٔ روزانه تمام شده"
            else:
                why = "سقف دقیقه‌ای؛ به‌زودی آزاد می‌شود"
        rows.append((kid, name, t - now, why))
    return sorted(rows, key=lambda r: r[2])


def blocked_count():
    return sum(1 for t in _blocked().values() if t > time.time())


def reset_model_cache():
    _blocked().clear()
    _reasons().clear()
    _list_models.clear()


def diagnose():
    """هر مدل را با یک درخواست بسیار کوتاه (بدون جست‌وجو) تست می‌کند و دلیل شکست را نشان می‌دهد."""
    _blocked().clear()
    _reasons().clear()
    keys = _get_keys()
    ok, info = groq_client.ping()
    st.markdown("**Groq (جست‌وجوی منابع)**")
    st.code(("✅ کار می‌کند" if ok else "❌ ") + (f" — {info}" if info else ""), language=None)
    if not keys:
        st.error("ابتدا کلید را وارد کنید.")
        return
    for i, k in enumerate(keys, 1):
        st.markdown(f"**کلید {fa(i)}** (…{k[-4:]})")
        try:
            models = _candidates(k)[:12]
        except Exception as exc:  # noqa: BLE001
            st.error(f"دریافت فهرست مدل‌ها ناموفق بود: {_brief(exc)}")
            continue
        client = genai.Client(api_key=k)
        rows, bar = [], st.progress(0)
        for j, m in enumerate(models, 1):
            short = m.replace("models/", "")
            _count_request()
            try:
                client.models.generate_content(model=m, contents="Reply with: OK")
                rows.append(f"✅ {short}")
            except Exception as exc:  # noqa: BLE001
                rows.append(f"❌ {short} — {_brief(exc)}")
            bar.progress(j / max(len(models), 1))
        bar.empty()
        # آزمایش جداگانهٔ جست‌وجوی وب (سهمیهٔ جدا از خود مدل)
        if models:
            _count_request()
            try:
                client.models.generate_content(
                    model=models[0], contents="Reply with: OK",
                    config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]))
                rows.append("🔎 جستجوی وب: ✅ کار می‌کند")
            except Exception as exc:  # noqa: BLE001
                rows.append(f"🔎 جستجوی وب: ❌ — {str(exc)[:400].replace(chr(10), ' ')}")
        st.code("\n".join(rows) or "مدلی پیدا نشد", language=None)
