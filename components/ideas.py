"""کارت «ایده‌های موضوعات دیپ‌دایو»."""
import datetime as dt

import streamlit as st

from core.ai import research_deep
from core.helpers import H, chip, esc


def render_ideas():
    ss = st.session_state
    with st.container(border=True):
        H('<div class="card-title">ایده‌های موضوعات دیپ‌دایو</div>')
        pub = st.date_input("تاریخ انتشار پیشنهادی",
                            value=dt.date.today() + dt.timedelta(days=3), key="pub_date")
        for idx, topic in enumerate(ss.deep_topics):
            with st.container(border=True):
                H(f'<div class="news-title">{esc(topic["title"])} {chip(topic["status"])}</div>')
                with st.container(key=f"keep_idea_{idx}"):
                    b_cal, b_scn = st.columns(2)
                    add_cal = b_cal.button(":material/calendar_month: تقویم", key=f"cal_{idx}")
                    add_scn = b_scn.button(":material/movie: سناریو", key=f"scn_{idx}")
                if add_cal:
                    ss.events = [e for e in ss.events if e["title"] != topic["title"]]
                    ss.events.append({"date": pub.isoformat(), "title": topic["title"]})
                    topic["status"] = "Approved"
                    ss.cal_year, ss.cal_month = pub.year, pub.month
                    st.rerun()
                if add_scn:
                    text = research_deep(topic["title"])
                    if text:
                        topic["scenario"] = text
                        st.rerun()
                if topic["scenario"]:
                    with st.expander("سناریوی کامل و تحقیق دیپ‌دایو", expanded=True):
                        view, edit = st.tabs([":material/visibility: نمایش", ":material/edit: ویرایش"])
                        with view:
                            st.markdown(topic["scenario"])
                        with edit:
                            edited = st.text_area("متن سناریو (مارک‌داون)", value=topic["scenario"],
                                                  height=420, key=f"scn_edit_{idx}")
                            if st.button(":material/save: ذخیره ویرایش", key=f"scn_save_{idx}"):
                                topic["scenario"] = edited
                                st.toast("ذخیره شد")
                                st.rerun()
