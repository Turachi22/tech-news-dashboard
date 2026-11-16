"""کارت «جریان کاری تأیید اخبار»: مراحل، کارت هر خبر، تأیید/رد/بررسی هوشمند و (در صفحهٔ اخبار) اسکریپت."""
import datetime as dt
import time

import streamlit as st

from core.ai import NEWS_PROMPT, ask_ai, build_followup_prompt
from core.export import DOCX_MIME, HAS_DOCX, make_docx
from core.helpers import H, chip, esc, fa
from core.state import (ARCHIVE_DAYS, KEEP_PREVIOUS_WEEKS, WEEKDAY_FA, current_week, days_left,
                        now_str, save_data)


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


def _add_version(item, question, text, secs=None):
    """هر تحقیق یا پاسخ تازه، یک نسخهٔ جدید زیر نسخه‌های قبلی می‌شود (هیچ نسخه‌ای بازنویسی نمی‌شود)."""
    versions = item.setdefault("research", [])
    versions.append({"v": len(versions) + 1, "ts": now_str(), "q": question, "text": text,
                     "model": st.session_state.get("active_model", ""), "secs": secs})
    save_data()


def _research_block(idx, item):
    """نسخه‌های تحقیق + کادر پرسش تکمیلی از Gemini."""
    versions = item.get("research") or []
    if not versions:
        return
    st.caption(f"🗂 آرشیف: {fa(len(versions))} نسخه · تا {fa(days_left(item))} روز دیگر نگه‌داری می‌شود "
               f"(پس از {fa(ARCHIVE_DAYS)} روز بدون فعالیت، خودکار حذف می‌شود)")
    for i, v in enumerate(versions):
        title = "بررسی اولیه" if not v.get("q") else v["q"][:60] + ("…" if len(v["q"]) > 60 else "")
        with st.expander(f"نسخهٔ {fa(v['v'])} — {title} · {fa(v['ts'])}", expanded=(i == len(versions) - 1)):
            st.markdown(v["text"])
            info = " · ".join(x for x in (v.get("model"), f"{fa(v['secs'])} ثانیه" if v.get("secs") else "") if x)
            if info:
                st.caption(info)

    with st.expander("💬 سؤال یا درخواست اطلاعات بیشتر"):
        with st.form(f"chat_{idx}", clear_on_submit=True):
            q = st.text_area("سؤال شما از Gemini", height=90,
                             placeholder="مثلاً: آمار دقیق‌تر بده / منبع این ادعا چیست؟ / از دید منتقدان بنویس")
            sent = st.form_submit_button("ارسال", type="primary")
        if sent and q.strip():
            t0 = time.time()
            text = ask_ai(build_followup_prompt(item, q.strip()))
            if text:
                _add_version(item, q.strip(), text, round(time.time() - t0, 1))
                st.rerun()


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
            if text:
                again = bool(item.get("research"))
                _add_version(item, "بررسی مجدد" if again else "", text, round(time.time() - t0, 1))
                if item["status"] == "Pending":
                    item["status"] = "Reviewing"
                st.rerun()
        _research_block(idx, item)

        if show_script and item["status"] == "Approved":
            _script_box(idx, item)


def _day_label(iso):
    try:
        d = dt.date.fromisoformat(iso)
        return f"📅 {WEEKDAY_FA[d.weekday()]} {fa(iso)}" + (" (امروز)" if d == dt.date.today() else "")
    except ValueError:
        return "📅 —"


def _indices(week):
    """شمارهٔ خبرهای یک هفته؛ جدیدترین روز اول، و خبرهای روزهای قبل پایین‌تر."""
    news = st.session_state.news_list
    idxs = [i for i, n in enumerate(news) if n.get("week") == week]
    return sorted(idxs, key=lambda i: news[i].get("added", ""), reverse=True)  # مرتب‌سازی پایدار است


def _render_items(idxs, show_script):
    news, last_day = st.session_state.news_list, None
    for i in idxs:
        day = news[i].get("added", "")
        if day != last_day:
            H(f'<div class="muted" style="margin:10px 0 4px">{_day_label(day)}</div>')
            last_day = day
        news_item(i, news[i], show_script)


def render_workflow(show_script=False):
    """جریان کاری هفتهٔ جاری."""
    news = st.session_state.news_list
    idxs = _indices(current_week())
    week_news = [news[i] for i in idxs]
    total = len(week_news)
    count = lambda s: sum(1 for n in week_news if n["status"] == s)  # noqa: E731
    done = count("Approved")
    pct = round(done / total * 100) if total else 0
    with st.container(border=True):
        H('<div class="card-title">جریان کاری تأیید اخبار (هفتهٔ جاری)</div>')
        H(f'<div class="progress"><div style="width:{pct}%"></div></div>'
          f'<div class="muted">{fa(done)} از {fa(total)} خبر تأیید شده · {fa(count("Rejected"))} رد شده</div>'
          '<div class="stepper">'
          f'<div class="step queue">در صف <b>{fa(count("Pending"))}</b></div><span class="arrow">←</span>'
          f'<div class="step review">بررسی <b>{fa(count("Reviewing"))}</b></div><span class="arrow">←</span>'
          f'<div class="step done">تأیید شده <b>{fa(done)}</b></div>'
          '</div>')
        if not idxs:
            st.caption("هنوز خبری برای این هفته نیست.")
        _render_items(idxs, show_script)


def render_previous_weeks(show_script=True):
    """پنجرهٔ جدا برای هفته‌های قبل (هر هفته یک زبانه). فقط KEEP_PREVIOUS_WEEKS هفته نگه داشته می‌شود."""
    cw = dt.date.fromisoformat(current_week())
    weeks = [(cw - dt.timedelta(weeks=k)).isoformat() for k in range(1, KEEP_PREVIOUS_WEEKS + 1)]
    weeks = [w for w in weeks if _indices(w)]
    if not weeks:
        return
    with st.container(border=True):
        H(f'<div class="card-title">📁 هفته‌های قبل (آرشیف {fa(KEEP_PREVIOUS_WEEKS)} هفته)</div>')
        tabs = st.tabs([f"{fa(w)} تا {fa((dt.date.fromisoformat(w) + dt.timedelta(days=6)).isoformat())}"
                        for w in weeks])
        for tab, w in zip(tabs, weeks):
            with tab:
                _render_items(_indices(w), show_script)
