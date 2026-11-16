"""ابزارهای کوچک و مشترک: اعداد فارسی، escape، چیپ وضعیت، عنوان صفحه."""
import html

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
