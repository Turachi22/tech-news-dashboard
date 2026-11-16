"""پیشنهاد خودکار روزانهٔ خبر: هر روز (با اولین باز شدن برنامه) سه خبر تازه به جریان کاری اضافه می‌شود."""
import datetime as dt

import streamlit as st

from core.ai import _get_keys, suggest_news
from core.state import save_data, week_start

DAILY_COUNT = 3          # تعداد خبر پیشنهادی در هر روز
SKIP_WEEKDAYS = {4}      # روزهای بدون پیشنهاد (۴ = جمعه، روز بررسی و نشر). برای پیشنهاد در جمعه: set()


def _done_today(iso):
    return any(n.get("auto") and n.get("added") == iso for n in st.session_state.news_list)


def ensure_daily_news():
    """اگر امروز هنوز پیشنهاد نگرفته‌ایم، یک‌بار (با یک درخواست) سه خبر تازه می‌گیرد و به صف اضافه می‌کند."""
    ss = st.session_state
    today = dt.date.today()
    iso = today.isoformat()
    if today.weekday() in SKIP_WEEKDAYS or _done_today(iso) or not _get_keys():
        return
    flag = f"_auto_tried_{iso}"
    if ss.get(flag):
        if st.button("🔄 دریافت دوبارهٔ پیشنهاد امروز", key="auto_retry"):
            ss[flag] = False
            st.rerun()
        return
    ss[flag] = True   # فقط یک تلاش در هر نشست؛ برای تلاش دوباره دکمهٔ بالا هست
    existing = [n["title"] for n in reversed(ss.news_list)]
    items, _sources = suggest_news(today, days=3, n=DAILY_COUNT, existing=existing)
    if items is None:
        return        # خطا قبلاً نمایش داده شده
    if not items:
        st.info("امروز خبر تازه‌ای در بازهٔ ۳ روز اخیر پیدا نشد.")
        return
    week = week_start(today).isoformat()
    for it in items[:DAILY_COUNT]:
        ss.news_list.append({
            "title": it["title"], "desc": f"{it['desc']} ({it['source']}، {it['date']})", "icon": "📰",
            "status": "Pending", "ai": "", "research": [], "added": iso, "week": week, "auto": True})
    save_data()
    st.toast(f"{len(items[:DAILY_COUNT])} خبر تازهٔ امروز اضافه شد.")
