"""کارت «جریان کاری تأیید اخبار»: مراحل، کارت هر خبر، تأیید/رد/بررسی هوشمند و (در صفحهٔ اخبار) اسکریپت."""
import datetime as dt
import time

import streamlit as st

from core.ai import NEWS_STRUCTURE, ask_ai, build_followup_prompt, research_conspiracies, research_news
from core import richtext
from core.export import DOCX_MIME, HAS_DOCX, make_docx
from core.helpers import H, chip, esc, fa, svg
from core.state import (ARCHIVE_DAYS, KEEP_PREVIOUS_WEEKS, WEEKDAY_FA, current_week, days_left,
                        now_str, save_data)


def _now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def script_section(idx, item):
    """(عنوان، توضیح، متن ساده، HTML رنگی) برای خروجی Word؛ آخرین نسخهٔ ذخیره‌شده."""
    meta = f"تاریخ تأیید: {item.get('decided') or '—'}"
    return (item["title"], meta, item.get("script", ""), item.get("script_html", ""))


def approved_sections():
    return [script_section(i, n) for i, n in enumerate(st.session_state.news_list)
            if n["status"] == "Approved" and script_section(i, n)[2].strip()]


def _script_box(idx, item):
    with st.expander(":material/edit_note: اسکریپت"):
        uid = item.setdefault("uid", richtext.new_uid())
        base = item.get("script_html") or richtext.md_to_html(item.get("script", ""))
        val = richtext.rich_editor(base, key=f"rte_{uid}_{item.get('rte_ver', 0)}", height=300)
        if isinstance(val, dict) and val.get("html") is not None:
            clean = richtext.sanitize(val["html"])
            if clean != item.get("script_html"):
                item["script_html"] = clean
                item["script"] = richtext.html_to_text(clean)
                item["script_saved"] = _now()
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
    st.caption(f":material/inventory_2: آرشیف: {fa(len(versions))} نسخه · تا {fa(days_left(item))} روز دیگر نگه‌داری می‌شود "
               f"(پس از {fa(ARCHIVE_DAYS)} روز بدون فعالیت، خودکار حذف می‌شود)")
    for i, v in enumerate(versions):
        title = "بررسی اولیه" if not v.get("q") else v["q"][:60] + ("…" if len(v["q"]) > 60 else "")
        with st.expander(f"نسخهٔ {fa(v['v'])} — {title} · {fa(v['ts'])}", expanded=False):
            st.markdown(v["text"])
            info = " · ".join(x for x in (v.get("model"), f"{fa(v['secs'])} ثانیه" if v.get("secs") else "") if x)
            if info:
                st.caption(info)

    if st.button(":material/travel_explore: بررسی عمیق‌تر نظریه‌های توطئه", key=f"cons_{idx}",
                 help="یک جست‌وجوی جداگانه فقط برای نظریه‌ها و شایعات؛ نتیجه به‌عنوان نسخهٔ جدید ذخیره می‌شود"):
        t0 = time.time()
        text = research_conspiracies(item["title"], item["desc"])
        if text:
            _add_version(item, "نظریه‌های توطئه (بررسی عمیق)", text, round(time.time() - t0, 1))
            st.rerun()

    with st.expander(":material/forum: سؤال یا درخواست اطلاعات بیشتر"):
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


MANUAL_RULES = (
    "تو ویراستار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و فقط مهم‌ترین و ضروری‌ترین "
    "اطلاعات را به فارسی روان بنویس. اعداد، تاریخ‌ها و نام‌ها را بیاور و هر ادعای مهم را با نام منبعش همراه کن. "
    "در پایان بخشی به نام «منابع» با لینک واقعی صفحه‌هایی که واقعاً خوانده‌ای بیاور؛ هرگز لینک نساز. "
    "اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)


def manual_prompt(item):
    """همان قالب اپ، ولی برای چسباندن در چت Gemini (لینک منابع را خود چت می‌نویسد)."""
    return MANUAL_RULES + NEWS_STRUCTURE.format(title=item["title"], desc=item["desc"])


def _save_manual(idx):
    ss = st.session_state
    text = (ss.get(f"manual_{idx}") or "").strip()
    if len(text) < 80:
        ss[f"manual_err_{idx}"] = True
        return
    item = ss.news_list[idx]
    _add_version(item, "نسخهٔ دستی (چت Gemini)", text, None)
    item["research"][-1]["model"] = "Gemini چت (دستی)"
    if item["status"] == "Pending":
        item["status"] = "Reviewing"
    ss[f"manual_err_{idx}"] = False
    ss[f"manual_{idx}"] = ""


def _manual_box(idx, item):
    """حالت دستی بدون API: پرامپت آماده را در چت Gemini بزنید و جواب را اینجا بچسبانید (بدون هیچ سهمیهٔ API)."""
    with st.expander(":material/content_paste: بدون API: پرامپت آماده + چسباندن جواب"):
        st.caption("۱) متن زیر را کپی کنید (آیکن کپی بالا-گوشهٔ کادر) · ۲) در چت Gemini بچسبانید "
                   "· ۳) جواب را کپی کرده و پایین بچسبانید و ذخیره کنید.")
        st.code(manual_prompt(item), language=None)
        st.text_area("جوابِ چت Gemini را اینجا بچسبانید", height=200, key=f"manual_{idx}")
        if st.session_state.get(f"manual_err_{idx}"):
            st.warning("متن خیلی کوتاه است؛ جواب کامل را بچسبانید.")
        st.button(":material/save: ذخیره به‌عنوان نسخهٔ جدید", key=f"manual_save_{idx}", type="primary",
                  on_click=_save_manual, args=(idx,))


def news_item(idx, item, show_script=False):
    status = item["status"]
    date_line = ""
    if status in ("Approved", "Rejected"):
        verb = "تأیید" if status == "Approved" else "رد"
        decided = item.get("decided", "")
        when = fa(decided) if decided else "ثبت نشده (یک‌بار دیگر دکمهٔ «" + verb + "» را بزنید)"
        date_line = f'<div class="muted" style="margin-top:4px">تاریخ {verb}: {when}</div>'
    with st.container(key=f"newscard_{idx}_{status}"):
        H('<div class="news-head">'
          f'<div class="avatar">{svg("news", 22)}</div>'
          f'<div><div class="news-title">{esc(item["title"])} {chip(status)}</div>'
          f'<div class="news-desc">{esc(item["desc"])}</div>{date_line}</div></div>')

        with st.container(key=f"keep_news_{idx}"):
            b_ok, b_no, b_ai = st.columns(3)
            ok = b_ok.button(":material/check: تأیید", key=f"app_{idx}", type="primary")
            no = b_no.button(":material/close: رد", key=f"rej_{idx}")
            ai = b_ai.button(":material/search: بررسی" if not item.get("research") else ":material/folder_open: تحقیق ثبت‌شده", key=f"rev_{idx}")
        if ok:
            item["status"], item["decided"] = "Approved", _now()
            st.rerun()
        if no:
            item["status"], item["decided"] = "Rejected", _now()
            st.rerun()
        has_research = bool(item.get("research"))
        redo_key = f"_redo_{idx}"
        if ai and has_research:
            # تحقیق قبلاً انجام شده؛ بدون تأیید، درخواست تازه‌ای مصرف نمی‌شود
            st.session_state[redo_key] = True
        if has_research and st.session_state.get(redo_key):
            st.info("برای این خبر قبلاً تحقیق انجام شده و نسخه‌های آن پایین‌تر هست. "
                    "بررسی مجدد یک درخواست جدید از سهمیه مصرف می‌کند.")
            c_yes, c_no = st.columns(2)
            go = c_yes.button(":material/replay: بله، نسخهٔ جدید بساز", key=f"redo_yes_{idx}", type="primary")
            if c_no.button("انصراف", key=f"redo_no_{idx}"):
                st.session_state[redo_key] = False
                st.rerun()
            if not go:
                ai = False
            else:
                st.session_state[redo_key] = False
                ai = True
        if ai:
            t0 = time.time()
            text = research_news(item["title"], item["desc"])
            if text:
                _add_version(item, "بررسی مجدد" if has_research else "", text, round(time.time() - t0, 1))
                if item["status"] == "Pending":
                    item["status"] = "Reviewing"
                st.rerun()
        _manual_box(idx, item)
        _research_block(idx, item)

        if show_script and item["status"] == "Approved":
            _script_box(idx, item)


def _day_label(iso):
    try:
        d = dt.date.fromisoformat(iso)
        return f"{svg('calendar', 16)} {WEEKDAY_FA[d.weekday()]} {fa(iso)}" + (" · امروز" if d == dt.date.today() else "")
    except ValueError:
        return "—"


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
            H(f'<div class="day-label">{_day_label(day)}</div>')
            last_day = day
        news_item(i, news[i], show_script)


def _week_range(w):
    d = dt.date.fromisoformat(w)
    return f"{fa(w)} تا {fa((d + dt.timedelta(days=6)).isoformat())}"


def _week_nav(week_label, prefix=""):
    """کلید «هفتهٔ قبل» (سمت چپ) و «هفتهٔ بعد» (سمت راست) با برچسب وسط. برمی‌گرداند: (شنبهٔ هفتهٔ انتخاب‌شده، offset)."""
    ss = st.session_state
    wk = f"{prefix}week_offset"
    off = max(-KEEP_PREVIOUS_WEEKS, min(0, ss.get(wk, 0)))
    ss[wk] = off
    week = (dt.date.fromisoformat(current_week()) + dt.timedelta(weeks=off)).isoformat()
    with st.container(key=f"keep_weeknav{prefix}"):
        c_next, c_mid, c_prev = st.columns([1, 2.4, 1])   # صفحه راست‌به‌چپ است: ستون اول سمت راست
        if c_next.button(":material/chevron_right: بعد", key=f"{prefix}wk_next", disabled=(off >= 0), use_container_width=True):
            ss[wk] = off + 1
            st.rerun()
        label = "هفتهٔ جاری" if off == 0 else f"{fa(-off)} هفته قبل"
        c_mid.markdown(f'<div class="wk-mid"><b>{label}</b><span>{week_label(week)}</span></div>',
                       unsafe_allow_html=True)
        if c_prev.button("قبل :material/chevron_left:", key=f"{prefix}wk_prev", disabled=(off <= -KEEP_PREVIOUS_WEEKS),
                         use_container_width=True):
            ss[wk] = off - 1
            st.rerun()
    return week, off


TAB_DEFS = [("done", "check_circle", "تأیید شده", lambda s: s == "Approved"),
            ("rej", "cancel", "رد شده", lambda s: s == "Rejected"),
            ("wait", "hourglass_empty", "در انتظار", lambda s: s not in ("Approved", "Rejected"))]


def render_workflow(show_script=False, nav=False, tabs=False):
    """جریان کاری. با nav=True بالای کارت کلید «هفتهٔ قبل / هفتهٔ بعد» هست و هفتهٔ جاری پیش‌فرض است.
    با tabs=True خبرها در سه دستهٔ «تأیید شده / رد شده / در انتظار» با شمارنده می‌آیند (خبرِ «در حال بررسی» هم
    در انتظار است؛ اگر بعد از بررسی رد شود، به «رد شده» می‌رود). انتخاب دسته با کلید ثابت حفظ می‌شود."""
    news = st.session_state.news_list
    with st.container(border=True):
        week, off = _week_nav(_week_range) if nav else (current_week(), 0)
        idxs = _indices(week)
        week_news = [news[i] for i in idxs]
        total = len(week_news)
        count = lambda s: sum(1 for n in week_news if n["status"] == s)  # noqa: E731
        done = count("Approved")
        pct = round(done / total * 100) if total else 0
        if not nav:
            H('<div class="card-title">اخبار هفتهٔ جاری</div>')
        waiting = total - done - count("Rejected")
        H('<div class="sum-row"><div>'
          f'<div class="sum-t">{fa(done)} از {fa(total)} خبر تأیید شده</div>'
          f'<div class="muted">{fa(count("Rejected"))} رد شده · {fa(waiting)} در انتظار</div></div>'
          f'<div class="progress"><div style="width:{pct}%"></div></div></div>')
        if not tabs:
            if not idxs:
                st.caption("خبری برای این هفته نیست.")
            _render_items(idxs, show_script)
            return
        by_key = {k: [i for i in idxs if m(news[i]["status"])] for k, _ic, _lb, m in TAB_DEFS}
        labels = {k: f":material/{ic}: {lb}  ·  {fa(len(by_key[k]))}" for k, ic, lb, _m in TAB_DEFS}
        keys = [d[0] for d in TAB_DEFS]
        if hasattr(st, "segmented_control"):
            pick = st.segmented_control("دسته", keys, default="done", key="news_tab",
                                        format_func=lambda k: labels[k], label_visibility="collapsed") or "done"
        else:  # نسخه‌های قدیمی‌تر Streamlit
            pick = st.radio("دسته", keys, key="news_tab", horizontal=True,
                            format_func=lambda k: labels[k], label_visibility="collapsed")
        if not by_key[pick]:
            st.caption("خبری در این دسته نیست.")
        _render_items(by_key[pick], show_script)
