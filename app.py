"""نقطهٔ ورود برنامه. فقط تنظیمات کلی، فهرست صفحه‌ها (منو) و مسیریابی اینجاست.

افزودن صفحهٔ جدید: یک فایل در views/ بسازید (با تابع render) و یک خط به ROUTES اضافه کنید.
"""
import streamlit as st

from pathlib import Path  # noqa: E402

try:
    from PIL import Image  # آیکن لوگو برای تب مرورگر و میان‌بر گوشی
    _ICON = Image.open(Path(__file__).resolve().parent / "static" / "icon-512.png")
except Exception:  # noqa: BLE001
    _ICON = "🚀"

st.set_page_config(page_title="داشبورد شخصی ساده", layout="wide", page_icon=_ICON)

from components.sidebar import render_sidebar  # noqa: E402
from core.auth import require_login  # noqa: E402
from core.pwa import inject_pwa  # noqa: E402
from core.state import init_state, save_data  # noqa: E402
from core.style import apply_css  # noqa: E402
from views import deep, home, news, settings, stats  # noqa: E402

ROUTES = [  # (کلید در آدرس، برچسب منو، تابع نمایش)
    ("home", ":material/home: خانه", home.render),
    ("news", ":material/newspaper: اخبار", news.render),
    ("deep", ":material/lightbulb: دیپ‌دایو", deep.render),
    ("stats", ":material/bar_chart: آمار", stats.render),
    ("settings", ":material/settings: تنظیمات", settings.render),
]

apply_css()
require_login()   # رمز ورود (اگر APP_PASSWORD در Secrets باشد)
inject_pwa()
init_state()
active = render_sidebar(ROUTES)
for key, _label, render in ROUTES:
    if key == active:
        render()
save_data()  # ذخیرهٔ خودکار در پایان هر اجرا
