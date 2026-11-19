"""صفحهٔ تنظیمات: تست کلیدها، بازنشانی داده‌ها."""
import streamlit as st

from core import feeds
from core.ai import diagnose
from core.auth import logout_button
from core.backup import backup_section
from core.helpers import header
from core.state import ARCHIVE_DAYS, DATA_FILE
from core.storage import remote_enabled, save_remote


def render():
    header("تنظیمات", "تنظیمات داشبورد")
    with st.container(border=True):
        ss = st.session_state
        if remote_enabled():
            st.success("ذخیره‌سازی دائمی (Gist) فعال است." + (f" آخرین ذخیره: {ss['last_remote_save']}"
                                                          if ss.get("last_remote_save") else ""))
        else:
            st.warning("فعلاً فقط ذخیرهٔ موقت روی سرور فعال است؛ با Reboot یا به‌روزرسانی کد ممکن است پاک شود. "
                       "برای ذخیرهٔ دائمی، GITHUB_TOKEN و GIST_ID را در Secrets بگذارید.")
        for key in ("storage_error", "local_save_error"):
            if ss.get(key):
                st.error(ss[key])
        st.caption(f"آرشیف تحقیق‌ها: {ARCHIVE_DAYS} روز پس از آخرین فعالیت هر خبر.")
        st.text_input("نام کانال یوتیوب", value="کانال ساده")
        st.selectbox("وضعیت بروزرسانی خودکار", ["فعال", "غیرفعال"])
        st.divider()
        logout_button()
        st.divider()
        backup_section()
        st.divider()
        if st.button(":material/science: تست کلیدها و مدل‌ها"):
            diagnose()
        if st.button(":material/rss_feed: تست منابع خبر (فیدها، Google News، Hacker News)"):
            with st.spinner("در حال دریافت از منابع (حدود ۲۰ تا ۳۰ ثانیه)..."):
                feeds.health_report()
        if st.button("بازنشانی همهٔ داده‌ها"):
            if remote_enabled():       # بدون پاک‌کردن Gist، داده‌های قدیمی بعد از بازنشانی دوباره بارگذاری می‌شوند
                try:
                    save_remote("{}")
                except Exception as exc:  # noqa: BLE001
                    st.error(f"پاک‌کردن نسخهٔ Gist ناموفق بود؛ بازنشانی انجام نشد: {str(exc)[:150]}")
                    st.stop()
            for k in ("news_list", "deep_topics", "events", "daily", "_saved_hash", "_remote_retry_after"):
                st.session_state.pop(k, None)
            DATA_FILE.unlink(missing_ok=True)
            st.rerun()
