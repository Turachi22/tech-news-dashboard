"""صفحهٔ خانه: ترکیب کارت‌ها. فقط چیدمان اینجاست؛ خود کارت‌ها در components/ هستند."""
import streamlit as st

from components.calendar_card import render_calendar
from components.ideas import render_ideas
from components.stats_card import render_stats
from components.workflow import render_workflow
from core.helpers import header


def render():
    header("داشبورد شخصی تولید محتوای تکنولوژی 🚀",
           "مدیریت هوشمند اخبار هفتگی و بخش دوم (دیپ‌دایو)")
    with st.container(key="layout_top"):
        col_flow, col_ideas = st.columns([2, 1], gap="medium")  # ستون اول = سمت چپ (و در موبایل بالاتر)
        with col_flow:
            render_workflow()
        with col_ideas:
            render_ideas()
    with st.container(key="layout_bottom"):
        col_stats, col_cal = st.columns([1.6, 1], gap="medium")
        with col_stats:
            render_stats()
        with col_cal:
            render_calendar()
