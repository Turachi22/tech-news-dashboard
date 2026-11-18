"""ظاهر برنامه (CSS) — تم «شیشه‌ای تیره، فیروزه‌ای».

برای تغییر ظاهر فقط فایل مربوط را ویرایش کنید:
- base.py       رنگ‌ها (متغیرهای :root؛ با عوض‌کردن --accent رنگ اصلی عوض می‌شود)، فونت، سایدبار و منو
- cards.py      کارت‌ها، دکمه‌ها، تأیید/رد، عنوان‌ها، کلید هفته
- news.py       جریان کاری اخبار: دسته‌ها، کارت خبر، برچسب‌ها، نشانگر سهمیه
- dashboard.py  آمار، تقویم، چیدمان کلی و موبایل
"""
import streamlit as st
import streamlit.components.v1 as components

from core.style.base import CSS_BASE
from core.style.cards import CSS_CARDS
from core.style.dashboard import CSS_DASHBOARD
from core.style.news import CSS_NEWS

FONT_URL = "https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap"

CSS = (CSS_BASE + CSS_CARDS + CSS_NEWS + CSS_DASHBOARD + "</style>\n").replace("__FONT__", FONT_URL)

# اگر @import داخل صفحه اعمال نشد، همین لینک مستقیم به <head> صفحهٔ میزبان اضافه می‌شود
_FONT_JS = """<script>
(function () {
  try {
    var d = window.parent.document;
    if (d.querySelector('link[data-sade-font]')) return;
    var l = d.createElement('link');
    l.rel = 'stylesheet'; l.href = '%s'; l.setAttribute('data-sade-font', '1');
    d.head.appendChild(l);
  } catch (e) {}
})();
</script>""" % FONT_URL


def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)
    components.html(_FONT_JS, height=0)

