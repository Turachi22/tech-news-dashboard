"""منوی کناری: دکمه‌های صفحه‌ها (از فهرست ROUTES در app.py) و پنل کلیدهای Gemini."""
import streamlit as st

from core.ai import DAILY_REQUEST_LIMIT, blocked_count, reset_model_cache, usage_today
from core.helpers import H, fa, logo_html


BRAND_CSS = """
<style>
.brand { text-align: center; margin: 2px 0 10px; }
.brand-logo {
    width: 100%; max-width: 160px; height: auto; display: block; margin: 0 auto;
    -webkit-mask-image: linear-gradient(to right, transparent 0, #000 11%, #000 89%, transparent 100%),
                        linear-gradient(to bottom, transparent 0, #000 11%, #000 89%, transparent 100%);
    -webkit-mask-composite: source-in;
    mask-image: linear-gradient(to right, transparent 0, #000 11%, #000 89%, transparent 100%),
                linear-gradient(to bottom, transparent 0, #000 11%, #000 89%, transparent 100%);
    mask-composite: intersect;
}
</style>
"""


def render_sidebar(routes):
    """routes: فهرست (کلید، برچسب منو، تابع نمایش). کلید صفحه در آدرس هم ذخیره می‌شود تا با رفرش به همان صفحه برگردید."""
    ss = st.session_state
    keys = [r[0] for r in routes]
    if "page" not in ss:
        qp = st.query_params.get("page")
        ss.page = qp if qp in keys else keys[0]

    with st.sidebar:
        H(BRAND_CSS + f'<div class="brand">{logo_html("brand-logo")}</div>')
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
            st.caption(f"درخواست‌های امروز: {fa(usage_today())} از {fa(DAILY_REQUEST_LIMIT)}")
            if blocked_count():
                st.caption(f"{fa(blocked_count())} مدل موقتاً به سقف رسیده‌اند")
            if st.button("🔄 بازنشانی فهرست مدل‌ها"):
                reset_model_cache()
                st.rerun()

    if ss.page not in keys:
        ss.page = keys[0]
    st.query_params["page"] = ss.page
    return ss.page
