"""کادر «اسکریپت» هر خبر (ویرایشگر رنگ/اندازه) و داده‌های خروجی Word."""
import streamlit as st

from core import richtext
from core.export import DOCX_MIME, HAS_DOCX, make_docx
from core.helpers import fa
from core.state import now_str, save_data


def script_section(idx, item):
    """(عنوان، توضیح، متن ساده، HTML رنگی) برای خروجی Word؛ آخرین نسخهٔ ذخیره‌شده."""
    meta = f"تاریخ تأیید: {item.get('decided') or '—'}"
    return (item["title"], meta, item.get("script", ""), item.get("script_html", ""))


def approved_sections():
    return [script_section(i, n) for i, n in enumerate(st.session_state.news_list)
            if n["status"] == "Approved" and script_section(i, n)[2].strip()]


def script_box(idx, item):
    with st.expander(":material/edit_note: اسکریپت"):
        uid = item.setdefault("uid", richtext.new_uid())
        base = item.get("script_html") or richtext.md_to_html(item.get("script", ""))
        val = richtext.rich_editor(base, key=f"rte_{uid}_{item.get('rte_ver', 0)}", height=300)
        if isinstance(val, dict) and val.get("html") is not None:
            clean = richtext.sanitize(val["html"])
            if clean != item.get("script_html"):
                item["script_html"] = clean
                item["script"] = richtext.html_to_text(clean)
                item["script_saved"] = now_str()
                save_data()
        saved = item.get("script_saved")
        st.caption(f"آخرین ذخیره: {fa(saved)}" if saved else
                   "متن را انتخاب کنید و اندازه یا رنگ بدهید؛ بعد داخل ویرایشگر «ذخیره» (یا Ctrl+S) را بزنید.")
        with st.container(key=f"keep_script_{idx}"):
            c_word, c_txt = st.columns(2)
            if HAS_DOCX:
                c_word.download_button(":material/download: Word", data=make_docx([script_section(idx, item)]),
                                       file_name=f"script_{idx + 1}.docx", mime=DOCX_MIME,
                                       key=f"dl_word_{idx}")
            c_txt.download_button(":material/download: متن", data=item.get("script", ""),
                                  file_name=f"script_{idx + 1}.txt", key=f"dl_txt_{idx}")
