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


def chip(status):
    return f'<span class="chip {STATUS_CHIP[status]}">{STATUS_FA[status]}</span>'


def header(title, sub):
    H(f'<div class="page-title">{title}</div><div class="page-sub">{sub}</div>')


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
