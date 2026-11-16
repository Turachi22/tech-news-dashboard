"""نقطهٔ ورود برنامه. فقط تنظیمات کلی، فهرست صفحه‌ها (منو) و مسیریابی اینجاست.

افزودن صفحهٔ جدید: یک فایل در views/ بسازید (با تابع render) و یک خط به ROUTES اضافه کنید.
"""
import streamlit as st

st.set_page_config(page_title="داشبورد تولید محتوای تکنولوژی", layout="wide", page_icon="🚀")

from components.sidebar import render_sidebar  # noqa: E402
from core.state import init_state, save_data  # noqa: E402
from core.style import apply_css  # noqa: E402
from views import deep, home, news, settings, stats  # noqa: E402

ROUTES = [  # (کلید در آدرس، برچسب منو، تابع نمایش)
    ("home", "🏠 خانه", home.render),
    ("news", "📰 اخبار", news.render),
    ("deep", "💡 دیپ‌دایو", deep.render),
    ("stats", "📊 آمار", stats.render),
    ("settings", "⚙️ تنظیمات", settings.render),
]

apply_css()
init_state()
active = render_sidebar(ROUTES)
for key, _label, render in ROUTES:
    if key == active:
        render()
save_data()  # ذخیرهٔ خودکار در پایان هر اجرا
