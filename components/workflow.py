"""کارت «جریان کاری تأیید اخبار»: مراحل، کارت هر خبر، تأیید/رد/بررسی هوشمند و (در صفحهٔ اخبار) اسکریپت."""
import datetime as dt
import time

import streamlit as st

from core.ai import NEWS_PROMPT, ask_ai
from core.export import DOCX_MIME, HAS_DOCX, make_docx
from core.helpers import H, chip, esc, fa
from core.state import save_data


def _now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def _save_script(idx):
    """هم با خارج‌شدن از کادر متن و هم با دکمهٔ «ذخیره» اجرا می‌شود."""
    ss = st.session_state
    item = ss.news_list[idx]
    item["script"] = ss.get(f"script_{idx}", "")
    item["script_saved"] = _now()
    save_data()


def script_section(idx, item):
    """(عنوان، توضیح، متن) برای خروجی Word؛ متن فعلی کادر را می‌خواند، حتی اگر ذخیره نشده باشد."""
    body = st.session_state.get(f"script_{idx}", item.get("script", ""))
    meta = f"تاریخ تأیید: {item.get('decided') or '—'}"
    return (item["title"], meta, body)


def approved_sections():
    return [script_section(i, n) for i, n in enumerate(st.session_state.news_list)
            if n["status"] == "Approved" and script_section(i, n)[2].strip()]


def _script_box(idx, item):
    with st.expander("📝 اسکریپت"):
        saved = item.get("script_saved")
        st.text_area("متن نهایی اسکریپت", value=item.get("script", ""), height=260,
                     key=f"script_{idx}", on_change=_save_script, args=(idx,))
        st.caption(f"آخرین ذخیره: {fa(saved)}" if saved else "هنوز ذخیره نشده. با خارج‌شدن از کادر، خودکار ذخیره می‌شود.")
        with st.container(key=f"keep_script_{idx}"):
            c_save, c_word, c_txt = st.columns(3)
            c_save.button("💾 ذخیره", key=f"save_script_{idx}", type="primary",
                          on_click=_save_script, args=(idx,))
            if HAS_DOCX:
                c_word.download_button("⬇️ Word", data=make_docx([script_section(idx, item)]),
                                       file_name=f"script_{idx + 1}.docx", mime=DOCX_MIME,
                                       key=f"dl_word_{idx}")
            c_txt.download_button("⬇️ متن", data=st.session_state.get(f"script_{idx}", item.get("script", "")),
                                  file_name=f"script_{idx + 1}.txt", key=f"dl_txt_{idx}")


def news_item(idx, item, show_script=False):
    status = item["status"]
    date_line = ""
    if status in ("Approved", "Rejected"):
        verb = "تأیید" if status == "Approved" else "رد"
        decided = item.get("decided", "")
        when = fa(decided) if decided else "ثبت نشده (یک‌بار دیگر دکمهٔ «" + verb + "» را بزنید)"
        date_line = f'<div class="muted" style="margin-top:4px">📅 تاریخ {verb}: {when}</div>'
    with st.container(border=True):
        H('<div class="news-head">'
          f'<div class="avatar">{item["icon"]}</div>'
          f'<div><div class="news-title">{esc(item["title"])} {chip(status)}</div>'
          f'<div class="news-desc">{esc(item["desc"])}</div>{date_line}</div></div>')

        with st.container(key=f"keep_news_{idx}"):
            b_ok, b_no, b_ai = st.columns(3)
            ok = b_ok.button("➕ تأیید", key=f"app_{idx}", type="primary")
            no = b_no.button("✖ رد", key=f"rej_{idx}")
            ai = b_ai.button("🔍 بررسی", key=f"rev_{idx}")
        if ok:
            item["status"], item["decided"] = "Approved", _now()
            st.rerun()
        if no:
            item["status"], item["decided"] = "Rejected", _now()
            st.rerun()
        if ai:
            t0 = time.time()
            text = ask_ai(NEWS_PROMPT.format(title=item["title"], desc=item["desc"]))
            st.session_state["last_ai_secs"] = round(time.time() - t0, 1)
            if text:
                item["ai"] = text
                if item["status"] == "Pending":
                    item["status"] = "Reviewing"
                st.rerun()
        if item["ai"]:
            secs = st.session_state.get("last_ai_secs")
            with st.expander("نتیجهٔ بررسی هوشمند" + (f" ({fa(secs)} ثانیه)" if secs else "")):
                st.markdown(item["ai"])

        if show_script and item["status"] == "Approved":
            _script_box(idx, item)


def render_workflow(show_script=False):
    news = st.session_state.news_list
    total = len(news)
    count = lambda s: sum(1 for n in news if n["status"] == s)  # noqa: E731
    done = count("Approved")
    pct = round(done / total * 100) if total else 0
    with st.container(border=True):
        H('<div class="card-title">جریان کاری تأیید اخبار</div>')
        H(f'<div class="progress"><div style="width:{pct}%"></div></div>'
          f'<div class="muted">{fa(done)} از {fa(total)} خبر تأیید شده · {fa(count("Rejected"))} رد شده</div>'
          '<div class="stepper">'
          f'<div class="step queue">در صف <b>{fa(count("Pending"))}</b></div><span class="arrow">←</span>'
          f'<div class="step review">بررسی <b>{fa(count("Reviewing"))}</b></div><span class="arrow">←</span>'
          f'<div class="step done">تأیید شده <b>{fa(done)}</b></div>'
          '</div>')
        for idx, item in enumerate(news):
            news_item(idx, item, show_script)
