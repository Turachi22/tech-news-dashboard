"""صفحهٔ تنظیمات: تست کلیدها، بازنشانی داده‌ها."""
import streamlit as st

from core.ai import diagnose
from core.helpers import header
from core.state import DATA_FILE


def render():
    header("تنظیمات", "تنظیمات داشبورد")
    with st.container(border=True):
        st.text_input("نام کانال یوتیوب", value="کانال ساده")
        st.selectbox("وضعیت بروزرسانی خودکار", ["فعال", "غیرفعال"])
        if st.button("🧪 تست کلیدها و مدل‌ها"):
            diagnose()
        if st.button("بازنشانی همهٔ داده‌ها"):
            for k in ("news_list", "deep_topics", "events"):
                st.session_state.pop(k, None)
            DATA_FILE.unlink(missing_ok=True)
            st.rerun()
