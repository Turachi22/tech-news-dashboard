"""وضعیت سهمیه و تست مدل‌ها/کلیدها (برای منوی کناری و تنظیمات)."""
import time

import streamlit as st
from google import genai
from google.genai import types

from core import groq_client
from core.ai.gemini_models import (_blocked, _brief, _candidates, _count_request, _get_keys, _list_models,
                                   _reasons)
from core.helpers import fa


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
    st.code(("کار می‌کند ✓" if ok else "خطا ✗ ") + (f" — {info}" if info else ""), language=None)
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
