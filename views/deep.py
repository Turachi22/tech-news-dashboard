"""صفحهٔ دیپ‌دایو: ایده‌ها + افزودن موضوع + تقویم."""
import streamlit as st

from components.calendar_card import render_calendar
from components.ideas import render_ideas
from core.helpers import header
from core.state import new_topic


def render():
    header("موضوعات دیپ‌دایو", "ایده‌های عمیق و مینی‌مستند")
    render_ideas()
    with st.form("add_topic", clear_on_submit=True):
        t = st.text_input("موضوع جدید")
        if st.form_submit_button("افزودن موضوع") and t.strip():
            st.session_state.deep_topics.append(new_topic(t.strip()))
            st.rerun()
    render_calendar()
