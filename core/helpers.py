"""ابزارهای کوچک و مشترک: اعداد فارسی، escape، چیپ وضعیت، عنوان صفحه."""
import base64
import html
from functools import lru_cache
from pathlib import Path

import streamlit as st

FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
MONTHS_FA = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
             "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]
WEEKDAYS_FA = ["ش", "ی", "د", "س", "چ", "پ", "ج"]  # هفته از شنبه
STATUS_FA = {"Pending": "در صف", "Reviewing": "در حال بررسی",
             "Approved": "تأیید شده", "Rejected": "رد شده"}
STATUS_CHIP = {"Pending": "chip-pending", "Reviewing": "chip-review",
               "Approved": "chip-done", "Rejected": "chip-rej"}


def fa(value):
    if isinstance(value, int):
        value = f"{value:,}".replace(",", "٬")
    return str(value).translate(FA_DIGITS)


def esc(text):
    return html.escape(str(text))


def H(markup):
    st.markdown(markup, unsafe_allow_html=True)


_PATHS = {
    "news": "M20 5v14H4V5zm0-2H4c-1.11 0-2 .89-2 2v14c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V5c0-1.11-.89-2-2-2m-2 12H6v2h12zm-8-8H6v6h4zm2 2h6V7h-6zm6 2h-6v2h6z",
    "calendar": "M19 3h-1V1h-2v2H8V1H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14c1.11 0 2-.89 2-2V5a2 2 0 0 0-2-2m0 16H5V9h14zm0-12H5V5h14z",
}


def svg(name, size=20):
    """آیکن خطی SVG (بدون وابستگی به ایموجی/فونت)."""
    return (f'<svg class="ico-svg" viewBox="0 0 24 24" width="{size}" height="{size}" fill="currentColor">'
            f'<path d="{_PATHS[name]}"/></svg>')


def chip(status):
    return f'<span class="chip {STATUS_CHIP[status]}">{STATUS_FA[status]}</span>'


def header(title, sub):
    H(f'<div class="page-head"><div class="page-title">{title}</div><div class="page-sub">{sub}</div></div>')


LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.webp"


@lru_cache(maxsize=1)
def _logo_uri():
    try:
        return "data:image/webp;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode()
    except OSError:
        return ""


def logo_html(css_class="logo"):
    """لوگوی ساده (سفید و سرخ، شفاف)؛ اگر فایل assets/logo.webp نبود، متن «ساده»."""
    uri = _logo_uri()
    return f'<img class="{css_class}" src="{uri}" alt="ساده">' if uri else "ساده"
