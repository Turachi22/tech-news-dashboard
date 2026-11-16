"""صفحهٔ خانه: ترکیب کارت‌ها. فقط چیدمان اینجاست؛ خود کارت‌ها در components/ هستند."""
import streamlit as st

from components.calendar_card import render_calendar
from components.ideas import render_ideas
from components.stats_card import render_stats
from components.workflow import render_workflow
from core.daily import ensure_daily_news
from core.helpers import H, logo_html


HERO_CSS = """
<style>
.hero { text-align: center; margin: 4px 0 26px; }
.hero-title { display: flex; align-items: center; justify-content: center; gap: 18px; flex-wrap: wrap; direction: rtl; }
.hero-title span { font-size: 2.7rem; font-weight: 800; color: #fff; line-height: 1.2; }
.hero-logo { height: 132px; width: auto; filter: drop-shadow(0 8px 22px rgba(0,0,0,.55)); }
.hero-sub { margin-top: 10px; font-size: .8rem; color: #a5b4fc; opacity: .9; }
.hero-sub i { font-style: normal; font-size: .85rem; margin-left: 4px; }
.brand-logo { width: 100%; max-width: 120px; height: auto; }
@media (max-width: 640px) {
    .hero-title { gap: 10px; }
    .hero-title span { font-size: 1.7rem; }
    .hero-logo { height: 84px; }
}
</style>
"""


def hero():
    """عنوان بزرگ «داشبورد شخصی [لوگوی ساده]» و زیرعنوان کوچک با آیکن کوچک."""
    H(HERO_CSS + '<div class="hero"><div class="hero-title">'
      f'<span>داشبورد شخصی</span>{logo_html("hero-logo")}</div>'
      '<div class="hero-sub"><i>🚀</i>مدیریت هوشمند اخبار هفتگی و بخش دوم (دیپ‌دایو)</div></div>')


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
