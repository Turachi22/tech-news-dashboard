"""کلید «هفتهٔ قبل / بعد» (هفتهٔ جاری و دو هفتهٔ قبل) برای اخبار و دیپ‌دایو."""
import datetime as dt

import streamlit as st

from core.helpers import fa
from core.state import KEEP_PREVIOUS_WEEKS, current_week


def week_range(w):
    d = dt.date.fromisoformat(w)
    return f"{fa(w)} تا {fa((d + dt.timedelta(days=6)).isoformat())}"


def week_nav(week_label, prefix=""):
    """کلید «هفتهٔ قبل» (سمت چپ) و «هفتهٔ بعد» (سمت راست) با برچسب وسط. برمی‌گرداند: (شنبهٔ هفتهٔ انتخاب‌شده، offset)."""
    ss = st.session_state
    wk = f"{prefix}week_offset"
    off = max(-KEEP_PREVIOUS_WEEKS, min(0, ss.get(wk, 0)))
    ss[wk] = off
    week = (dt.date.fromisoformat(current_week()) + dt.timedelta(weeks=off)).isoformat()
    with st.container(key=f"keep_weeknav{prefix}"):
        c_next, c_mid, c_prev = st.columns([1, 2.4, 1])   # صفحه راست‌به‌چپ است: ستون اول سمت راست
        if c_next.button(":material/chevron_right: بعد", key=f"{prefix}wk_next", disabled=(off >= 0), use_container_width=True):
            ss[wk] = off + 1
            st.rerun()
        label = "هفتهٔ جاری" if off == 0 else f"{fa(-off)} هفته قبل"
        c_mid.markdown(f'<div class="wk-mid"><b>{label}</b><span>{week_label(week)}</span></div>',
                       unsafe_allow_html=True)
        if c_prev.button("قبل :material/chevron_left:", key=f"{prefix}wk_prev", disabled=(off <= -KEEP_PREVIOUS_WEEKS),
                         use_container_width=True):
            ss[wk] = off - 1
            st.rerun()
    return week, off
