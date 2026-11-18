"""نسخهٔ آفلاین فقط‌خواندنی برای برنامهٔ موبایل (پوستهٔ PWA در docs/).

هر بار برنامه با اینترنت و بعد از ورود باز شود و متن‌های ذخیره‌شده تغییر کرده باشند، یک نسخهٔ سبک از آن‌ها
(تحقیق خبرها، اسکریپت‌ها، سناریو و نریشن دیپ‌دایو) با postMessage به پوستهٔ نصب‌شده فرستاده می‌شود و پوسته
آن را در حافظهٔ گوشی (IndexedDB) نگه می‌دارد. وقتی اینترنت قطع باشد، پوسته صفحهٔ خوانش آفلاین را نشان می‌دهد.

- فقط به آدرس WRAPPER_ORIGIN فرستاده می‌شود (آدرس GitHub Pages شما: https://<نام‌کاربری>.github.io).
  اگر پوسته را روی آدرس دیگری گذاشته‌اید، فقط همین یک خط را عوض کنید.
- داده روی گوشی رمز ندارد (رمز برنامه فقط روی سرور است).
"""
import hashlib
import json

import streamlit as st
import streamlit.components.v1 as components

WRAPPER_ORIGIN = "https://mossawikian.github.io"
MAX_RESEARCH_VERSIONS = 6      # برای هر خبر فقط آخرین نسخه‌ها (حجم کم)


def build_snapshot():
    ss = st.session_state
    news = []
    for n in ss.get("news_list", []):
        research = [{"ts": v.get("ts", ""), "q": v.get("q", ""), "text": v.get("text", "")}
                    for v in (n.get("research") or [])][-MAX_RESEARCH_VERSIONS:]
        if not research and not n.get("script"):
            continue
        news.append({"title": n.get("title", ""), "status": n.get("status", ""), "week": n.get("week", ""),
                     "added": n.get("added", ""), "research": research,
                     "script": n.get("script", ""), "script_html": n.get("script_html", "")})
    deep = []
    for t in ss.get("deep_topics", []):
        if not (t.get("scenario") or t.get("narration") or t.get("narration_html")):
            continue
        deep.append({"title": t.get("title", ""), "status": t.get("status", ""), "week": t.get("week", ""),
                     "scenario": t.get("scenario", ""), "narration": t.get("narration", ""),
                     "narration_html": t.get("narration_html", "")})
    return {"v": 1, "news": news, "deep": deep}


def _js_json(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def sync_offline_copy():
    """فقط وقتی محتوا تغییر کرده باشد، نسخهٔ آفلاین را به پوسته می‌فرستد."""
    ss = st.session_state
    snap = build_snapshot()
    digest = hashlib.md5(_js_json(snap).encode("utf-8")).hexdigest()
    if ss.get("_offline_hash") == digest:
        return
    ss["_offline_hash"] = digest
    payload = _js_json({"type": "sade-offline", "digest": digest, "data": snap})
    components.html(
        "<script>(function(){var m=" + payload + ";"
        "[window.top,window.parent].forEach(function(w){try{w.postMessage(m," + json.dumps(WRAPPER_ORIGIN) + ");}catch(e){}});"
        "})();</script>", height=0)
