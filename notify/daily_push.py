"""اعلان روزانهٔ ۳ تیتر برتر خبر به گوشی (Web Push)؛ در GitHub Actions اجرا می‌شود.

مراحل: جمع‌آوری خبر از همان فیدهای برنامه (بدون سهمیهٔ جست‌وجو) ← انتخاب ۳ خبر برتر از حوزه‌های متفاوت
← ترجمهٔ فارسی با یک فراخوان Gemini (اگر کلید نبود یا خطا شد، تیتر انگلیسی) ← ارسال ۳ اعلان جدا.
متغیرهای محیطی (Secrets): VAPID_PRIVATE_KEY، PUSH_SUBSCRIPTION (یک شیء JSON یا فهرستی از آن‌ها)، GEMINI_API_KEY (اختیاری).
"""
import datetime as dt
import json
import os
import sys
import time
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# core.feeds.collect از streamlit فقط برای کش نشست استفاده می‌کند؛ اینجا یک جانشین ساده کافی است.
_st = types.ModuleType("streamlit")
_st.session_state = {}
sys.modules.setdefault("streamlit", _st)

from core.feeds import collect  # noqa: E402
from core.feeds.sources import DOMAIN_FA  # noqa: E402

COUNT = 3
MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.6-flash"]
SITE = "https://mossawikian.github.io/tech-news-dashboard/"


def pick_top(cands, n=COUNT):
    """n خبر برتر؛ ابتدا از حوزه‌های متفاوت (cands از قبل بر اساس امتیاز مرتب است)."""
    out, used = [], set()
    for c in cands:
        if c["domain"] not in used:
            out.append(c)
            used.add(c["domain"])
        if len(out) == n:
            return out
    for c in cands:
        if c not in out:
            out.append(c)
        if len(out) == n:
            break
    return out


def translate(titles):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        print("GEMINI_API_KEY تنظیم نشده؛ تیترها انگلیسی می‌ماند.")
        return titles
    prompt = ("Translate these English tech news headlines into natural, concise Persian (Farsi) headlines. "
              "Keep product and company names in English. Return ONLY a JSON array of exactly "
              f"{len(titles)} strings in the same order.\n" + json.dumps(titles, ensure_ascii=False))
    try:   # همان کتابخانه‌ای که خود برنامه استفاده می‌کند؛ پس هر قالبی از کلید که در برنامه کار می‌کند اینجا هم کار می‌کند
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
    except Exception as exc:  # noqa: BLE001
        print(f"google-genai در دسترس نیست: {exc}")
        return titles
    for model in MODELS:
        try:
            resp = client.models.generate_content(
                model=model, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2))
            arr = json.loads(resp.text)
            if isinstance(arr, list) and len(arr) == len(titles) and all(isinstance(x, str) and x.strip() for x in arr):
                return [x.strip() for x in arr]
        except Exception as exc:  # noqa: BLE001
            print(f"ترجمه با {model} ناموفق: {type(exc).__name__}: {str(exc)[:120]}")
    return titles


def get_news():
    today = dt.datetime.now(dt.timezone.utc).date()
    for days in (1, 3):
        cands, _ = collect(today - dt.timedelta(days=days), today, refresh=True)
        top = pick_top(cands)
        if len(top) >= COUNT:
            return top
    return top


def subscriptions():
    raw = os.environ.get("PUSH_SUBSCRIPTION", "").strip()
    if not raw:
        sys.exit("PUSH_SUBSCRIPTION خالی است (کد اشتراک را در Secrets بگذارید).")
    data = json.loads(raw)
    return data if isinstance(data, list) else [data]


def main():
    from pywebpush import WebPushException, webpush

    priv = os.environ.get("VAPID_PRIVATE_KEY", "").strip()
    if not priv:
        sys.exit("VAPID_PRIVATE_KEY خالی است.")
    subs = subscriptions()
    top = get_news()
    if not top:
        sys.exit("هیچ خبری پیدا نشد.")
    fa = translate([c["title"] for c in top])
    print(f"{len(top)} خبر انتخاب شد.")
    failed = 0
    for i, (c, title) in enumerate(zip(top, fa), 1):
        dom = DOMAIN_FA.get(c["domain"], "")
        payload = {"title": f"📰 خبر {i} از {len(top)}" + (f" · {dom}" if dom else ""),
                   "body": title, "tag": f"sade-{dt.date.today().isoformat()}-{i}", "url": SITE}
        for sub in subs:
            try:
                webpush(subscription_info=sub, data=json.dumps(payload, ensure_ascii=False),
                        vapid_private_key=priv, vapid_claims={"sub": SITE}, ttl=6 * 3600)
                print(f"ارسال شد {i}: {title[:60]}")
            except WebPushException as exc:
                failed += 1
                code = getattr(exc.response, "status_code", None)
                print(f"ارسال ناموفق ({code}): {exc}")
                if code in (404, 410):
                    print("اشتراک منقضی شده؛ صفحهٔ notify.html را دوباره باز و کد جدید را در Secrets بگذارید.")
        time.sleep(2)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
