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
.hero { text-align: center; margin: 6px 0 28px; }
.hero-title { font-size: 3.4rem; font-weight: 800; color: #fff; line-height: 1.25; direction: rtl;
              text-shadow: 0 4px 24px rgba(99,102,241,.45); }
.hero-sub { margin-top: 10px; font-size: .8rem; color: #a5b4fc; opacity: .9; }
.hero-sub i { font-style: normal; font-size: .85rem; margin-left: 4px; }
@media (max-width: 640px) { .hero-title { font-size: 2.1rem; } }
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
