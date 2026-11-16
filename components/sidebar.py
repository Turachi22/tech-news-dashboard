"""منوی کناری: دکمه‌های صفحه‌ها (از فهرست ROUTES در app.py) و پنل کلیدهای Gemini."""
import streamlit as st

from core.ai import DAILY_REQUEST_LIMIT, blocked_count, quota_status, reset_model_cache, usage_today
from core.helpers import H, esc, fa, logo_html


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


def _wait_text(secs):
    if secs < 90:
        return f"{fa(int(secs))} ثانیه"
    if secs < 5400:
        return f"{fa(round(secs / 60))} دقیقه"
    return f"{fa(round(secs / 3600))} ساعت"


def _quota_box():
    """نشانگر کوچک وضعیت سهمیه: مصرف امروز + مدل‌های منتظر سهمیه و زمان آزاد شدن."""
    used, limit = usage_today(), DAILY_REQUEST_LIMIT
    pct = min(used / limit, 1.0) if limit else 0
    color = "#34d399" if pct < .6 else ("#fbbf24" if pct < .9 else "#f87171")
    rows = quota_status()
    waiting = "".join(
        f'<div class="q-row"><b>{esc(m.replace("models/", "") or "کلید …" + k)}</b>'
        f'<span>{esc(why)} · {_wait_text(t)}</span></div>' for k, m, t, why in rows[:6])
    H("""<style>
.qbox { border: 1px solid rgba(255,255,255,.12); border-radius: 12px; padding: 10px 12px; margin: 4px 0 10px;
        background: rgba(255,255,255,.04); font-size: .8rem; direction: rtl; }
.q-bar { height: 6px; border-radius: 6px; background: rgba(255,255,255,.12); margin: 6px 0 2px; overflow: hidden; }
.q-fill { height: 100%; border-radius: 6px; }
.q-row { display: flex; flex-direction: column; margin-top: 6px; padding-top: 6px;
         border-top: 1px dashed rgba(255,255,255,.12); }
.q-row span { opacity: .75; font-size: .72rem; }
</style>""" + f'<div class="qbox">📊 درخواست امروز: <b>{fa(used)}</b> از {fa(limit)}'
      f'<div class="q-bar"><div class="q-fill" style="width:{int(pct * 100)}%;background:{color}"></div></div>'
      + (f'<div style="margin-top:6px">⏳ منتظر سهمیه: {fa(len(rows))}</div>{waiting}' if rows
         else '<div style="margin-top:6px;opacity:.75">همهٔ مدل‌ها آمادهٔ کارند ✅</div>')
      + '</div>')


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
        _quota_box()
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
