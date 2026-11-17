"""صفحهٔ خانه: ترکیب کارت‌ها. فقط چیدمان اینجاست؛ خود کارت‌ها در components/ هستند."""
import streamlit as st

from components.calendar_card import render_calendar
from components.ideas import render_ideas
from components.stats_card import render_stats
from components.workflow import render_workflow
from core.daily import ensure_daily_news
from core.helpers import H


HERO_CSS = """
<style>
.hero { text-align: center; margin: 4px 0 26px; }
.hero-title { font-size: 3rem; font-weight: 800; line-height: 1.3; direction: rtl;
              background: linear-gradient(90deg, #5eead4, #38bdf8); -webkit-background-clip: text;
              background-clip: text; color: transparent; }
@media (max-width: 640px) { .hero-title { font-size: 2rem; } }
</style>
"""


def hero():
    """فقط عنوان بزرگ «داشبورد شخصی ساده»."""
    H(HERO_CSS + '<div class="hero"><div class="hero-title">داشبورد شخصی ساده</div>'
      '</div>')


def render():
    hero()
    ensure_daily_news()
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
