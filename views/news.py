"""صفحهٔ اخبار: جریان کاری + اسکریپت خبرهای تأییدشده + خروجی Word + افزودن خبر."""
import streamlit as st

from components.workflow import approved_sections, render_workflow
from core.export import DOCX_MIME, HAS_DOCX, make_docx
from core.helpers import header


def render():
    header("اخبار داغ هفته", "بررسی، تأیید یا ردِ خبرهای پیشنهادی")
    render_workflow(show_script=True)

    sections = approved_sections()
    if sections:
        if HAS_DOCX:
            st.download_button("⬇️ دانلود همهٔ اسکریپت‌ها (Word)", data=make_docx(sections),
                               file_name="scripts.docx", mime=DOCX_MIME, key="dl_word_all")
        else:
            st.info("برای خروجی Word، «python-docx» را به requirements.txt اضافه کنید.")

    with st.form("add_news", clear_on_submit=True):
        t = st.text_input("عنوان خبر جدید")
        d = st.text_input("توضیح کوتاه")
        if st.form_submit_button("افزودن خبر") and t.strip():
            st.session_state.news_list.append(
                {"title": t.strip(), "desc": d.strip(), "icon": "📰", "status": "Pending", "ai": "", "research": []})
            st.rerun()
