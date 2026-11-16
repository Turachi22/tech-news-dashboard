"""رمز ورود ساده با گزینهٔ «این دستگاه را به یاد داشته باش».

- رمز در Streamlit Secrets با نام APP_PASSWORD گذاشته می‌شود (در کد یا GitHub نیست).
- اگر APP_PASSWORD تنظیم نشده باشد، برنامه قفل نمی‌شود (تا ناخواسته از دسترس خارج نشوید).
- «به یاد داشتن»: یک کوکی امضاشده (HMAC از رمز؛ خود رمز ذخیره نمی‌شود) ۱۸۰ روز روی همان دستگاه می‌ماند.
  با عوض کردن رمز در Secrets، کوکی همهٔ دستگاه‌ها خودکار بی‌اعتبار می‌شود.
- پنج رمز اشتباه پشت‌سرهم → یک دقیقه قفل.
"""
import hashlib
import hmac
import time

import streamlit as st
import streamlit.components.v1 as components

COOKIE = "sade_auth"
COOKIE_DAYS = 180
MAX_FAILS = 5
LOCK_SECONDS = 60


def _password():
    try:
        return str(st.secrets.get("APP_PASSWORD", "") or "")
    except Exception:  # noqa: BLE001
        return ""


def _token(password):
    return hmac.new(password.encode("utf-8"), b"sade-remember-v1", hashlib.sha256).hexdigest()


@st.cache_resource
def _fails():
    return {"n": 0, "until": 0.0}


def _cookie_js(value, days):
    secs = days * 86400 if value else 0
    components.html(
        f"""<script>
        document.cookie = "{COOKIE}={value}; max-age={secs}; path=/; SameSite=None; Secure; Partitioned";
        </script>""", height=0)


def _flush_cookie_flags(token):
    ss = st.session_state
    if ss.pop("_set_cookie", False):
        _cookie_js(token, COOKIE_DAYS)
    if ss.pop("_clear_cookie", False):
        _cookie_js("", 0)


def require_login():
    """در ابتدای app.py صدا زده می‌شود؛ تا ورود موفق، بقیهٔ برنامه اجرا نمی‌شود (و هیچ درخواستی به Gemini نمی‌رود)."""
    ss = st.session_state
    pw = _password()
    if not pw:
        return
    tok = _token(pw)

    if ss.get("auth_ok"):
        _flush_cookie_flags(tok)
        return

    try:
        saved = st.context.cookies.get(COOKIE, "")
    except Exception:  # noqa: BLE001
        saved = ""
    if saved and hmac.compare_digest(saved, tok):
        ss["auth_ok"] = True
        return

    _flush_cookie_flags(tok)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown("<div style='height:12vh'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center'>🔒 داشبورد شخصی ساده</h3>", unsafe_allow_html=True)
        with st.form("login"):
            typed = st.text_input("رمز عبور", type="password")
            remember = st.checkbox("این دستگاه را به یاد داشته باش", value=True)
            go = st.form_submit_button("ورود", type="primary", use_container_width=True)
        if go:
            f = _fails()
            now = time.time()
            if now < f["until"]:
                st.error(f"تلاش‌های اشتباه زیاد بود؛ {int(f['until'] - now)} ثانیهٔ دیگر دوباره امتحان کنید.")
            elif hmac.compare_digest(typed.encode("utf-8"), pw.encode("utf-8")):
                f["n"] = 0
                ss["auth_ok"] = True
                ss["_set_cookie"] = bool(remember)
                st.rerun()
            else:
                f["n"] += 1
                if f["n"] >= MAX_FAILS:
                    f["n"], f["until"] = 0, now + LOCK_SECONDS
                st.error("رمز اشتباه است.")
    st.stop()


def logout_button():
    """دکمهٔ خروج (برای صفحهٔ تنظیمات): خروج + فراموش کردن این دستگاه."""
    if not _password():
        st.caption("رمز ورود فعال نیست (APP_PASSWORD در Secrets تنظیم نشده).")
        return
    if st.button("🔒 خروج و فراموش کردن این دستگاه", key="logout"):
        st.session_state["auth_ok"] = False
        st.session_state["_clear_cookie"] = True
        st.rerun()
