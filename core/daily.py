"""پیشنهاد خودکار روزانهٔ خبر.

قواعد برای صرفه‌جویی در سهمیه:
- هر روز فقط یک‌بار خودکار جستجو می‌شود (حتی اگر برنامه چندبار باز شود یا همهٔ مدل‌ها در انتظار سهمیه باشند).
  وضعیت تلاش در داده‌های ذخیره‌شده می‌ماند، پس با باز کردن دوبارهٔ اپ جستجوی تازه‌ای شروع نمی‌شود.
- اگر امروز سه خبر اضافه شده باشد، دیگر جستجو نمی‌شود.
- مدل ۵ خبر می‌آورد؛ سه تا امروز اضافه می‌شود و بقیه در «ذخیره» می‌ماند و فردا بدون جستجو استفاده می‌شود
  (به شرط آنکه هنوز در بازهٔ ۳ روز اخیر باشد).
- تلاش دوباره فقط با دکمهٔ دستی انجام می‌شود.
"""
import datetime as dt

import streamlit as st

from core.ai import _get_keys, suggest_news
from core.state import save_data, week_start

DAILY_COUNT = 3          # تعداد خبر اضافه‌شده در هر روز
FETCH_COUNT = 6          # تعداد خبر درخواستی در هر جستجو (مازاد برای روزهای بعد ذخیره می‌شود)
WINDOW_DAYS = 3
SKIP_WEEKDAYS = {4}      # روزهای بدون پیشنهاد (۴ = جمعه). برای پیشنهاد در جمعه: set()


def _done_today(iso):
    return any(n.get("auto") and n.get("added") == iso for n in st.session_state.news_list)


def _add(items, today, iso):
    ss = st.session_state
    week = week_start(today).isoformat()
    for it in items:
        ss.news_list.append({
            "title": it["title"], "desc": f"{it['desc']} ({it['source']}، {it['date']})", "icon": "📰",
            "status": "Pending", "ai": "", "research": [], "added": iso, "week": week, "auto": True})


def _usable_reserve(today):
    """خبرهای ذخیره‌ای که هنوز در بازهٔ ۳ روز اخیر هستند و تکراری نیستند."""
    ss = st.session_state
    start = (today - dt.timedelta(days=WINDOW_DAYS)).isoformat()
    have = {n["title"] for n in ss.news_list}
    return [r for r in ss.daily.get("reserve", []) if r.get("date", "") >= start and r["title"] not in have]


def ensure_daily_news():
    ss = st.session_state
    today = dt.date.today()
    iso = today.isoformat()
    if today.weekday() in SKIP_WEEKDAYS or _done_today(iso):
        return

    # ۱) اول از خبرهای ذخیره‌شدهٔ روزهای قبل استفاده کن (بدون هیچ درخواستی)
    reserve = _usable_reserve(today)
    if len(reserve) >= DAILY_COUNT:
        _add(reserve[:DAILY_COUNT], today, iso)
        ss.daily["reserve"] = reserve[DAILY_COUNT:]
        save_data()
        st.toast(f"{DAILY_COUNT} خبر از ذخیرهٔ روزهای قبل اضافه شد.")
        return

    if not _get_keys():
        return

    # ۲) فقط یک تلاش خودکار در روز (ماندگار؛ با بازکردن دوبارهٔ اپ تکرار نمی‌شود)
    if ss.daily.get("tried") == iso:
        st.caption("پیشنهاد امروز هنوز دریافت نشده (سهمیه یا خطا). برای تلاش دوباره دکمه را بزنید.")
        if st.button(":material/refresh: دریافت دوبارهٔ پیشنهاد امروز", key="auto_retry"):
            ss.daily["tried"] = ""
            st.rerun()
        return
    ss.daily["tried"] = iso
    save_data()

    existing = [n["title"] for n in reversed(ss.news_list)]
    items, _sources = suggest_news(today, days=WINDOW_DAYS, n=FETCH_COUNT, existing=existing)
    if items is None:
        return        # خطا قبلاً نمایش داده شده
    pool = reserve + [i for i in items if i["title"] not in {r["title"] for r in reserve}]
    if not pool:
        st.info("امروز خبر تازه‌ای در بازهٔ ۳ روز اخیر پیدا نشد.")
        return
    _add(pool[:DAILY_COUNT], today, iso)
    ss.daily["reserve"] = pool[DAILY_COUNT:]
    save_data()
    st.toast(f"{len(pool[:DAILY_COUNT])} خبر تازهٔ امروز اضافه شد.")
