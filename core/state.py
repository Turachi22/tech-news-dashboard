"""دادهٔ برنامه: مقادیر پیش‌فرض، ذخیره و بارگذاری (data.json)."""
import copy
import datetime as dt
import json
from pathlib import Path

import streamlit as st

NEWS_DEFAULT = [
    {"title": "ربات‌های انسان‌نما با یادگیری شهودی",
     "desc": "قابلیت یادگیری کارهای خانه با مشاهدهٔ رفتار انسان.",
     "icon": "🤖", "status": "Pending", "ai": ""},
    {"title": "سیگنال‌های مرموز فضایی",
     "desc": "کشف امواج رادیویی ناشناخته از لبهٔ منظومهٔ شمسی.",
     "icon": "📡", "status": "Pending", "ai": ""},
    {"title": "بافت‌های زیستی چاپ‌شده سه‌بعدی",
     "desc": "ترمیم خودکار آسیب‌های بافتی داخل بدن.",
     "icon": "🧬", "status": "Pending", "ai": ""},
]
DEEP_DEFAULT = [
    {"title": "رازهای پنهان الگوریتم‌های کلود شانون", "status": "Pending", "scenario": ""},
    {"title": "تکنولوژی فراموش‌شدهٔ باتری‌های حالت جامد", "status": "Pending", "scenario": ""},
    {"title": "پشت پردهٔ پروژه‌های محرمانهٔ فضایی مهار انرژی خورشیدی", "status": "Pending", "scenario": ""},
]


DATA_FILE = Path(__file__).resolve().parent.parent / "data.json"


def load_data():
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def save_data():
    ss = st.session_state
    try:
        DATA_FILE.write_text(
            json.dumps({"news_list": ss.news_list, "deep_topics": ss.deep_topics, "events": ss.events},
                       ensure_ascii=False, indent=1),
            encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def init_state():
    ss = st.session_state
    today = dt.date.today()
    saved = load_data() if "news_list" not in ss else {}
    ss.setdefault("news_list", saved.get("news_list") or copy.deepcopy(NEWS_DEFAULT))
    ss.setdefault("deep_topics", saved.get("deep_topics") or copy.deepcopy(DEEP_DEFAULT))
    ss.setdefault("events", saved.get("events") or [])
    ss.setdefault("cal_year", today.year)
    ss.setdefault("cal_month", today.month)
    ss.setdefault("views", [120, 250, 180, 300, 450, 380, 520])
    ss.setdefault("total_views", 12424)
