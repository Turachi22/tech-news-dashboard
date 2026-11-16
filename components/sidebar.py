"""منوی کناری: دکمه‌های صفحه‌ها (از فهرست ROUTES در app.py) و پنل کلیدهای Gemini."""
import streamlit as st

from core.ai import blocked_count, reset_model_cache
from core.helpers import H, fa


def render_sidebar(routes):
    """routes: فهرست (کلید، برچسب منو، تابع نمایش). کلید صفحه در آدرس هم ذخیره می‌شود تا با رفرش به همان صفحه برگردید."""
    ss = st.session_state
    keys = [r[0] for r in routes]
    if "page" not in ss:
        qp = st.query_params.get("page")
        ss.page = qp if qp in keys else keys[0]

    with st.sidebar:
        H('<div class="brand">ساده</div>')
        for key, label, _ in routes:
            if st.button(label, key=f"nav_{key}", type="primary" if ss.page == key else "secondary"):
                ss.page = key
                st.rerun()
        st.markdown("---")
        with st.expander("🔑 Gemini"):
            st.text_input("کلید اول", type="password", key="api_key")
            st.text_input("کلید دوم (اختیاری)", type="password", key="api_key2")
            if ss.get("active_model"):
                st.caption(f"مدل فعال: {ss.active_model.replace('models/', '')}")
            if blocked_count():
                st.caption(f"{fa(blocked_count())} مدل موقتاً به سقف رسیده‌اند")
            if st.button("🔄 بازنشانی فهرست مدل‌ها"):
                reset_model_cache()
                st.rerun()

    if ss.page not in keys:
        ss.page = keys[0]
    st.query_params["page"] = ss.page
    return ss.page
