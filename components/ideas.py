"""کارت «ایده‌های موضوعات دیپ‌دایو»: سناریو (نمایش) + ویرایش فقط متن نریشن + هفته‌های جاری و دو هفتهٔ قبل."""
import datetime as dt
import re

import streamlit as st

from components.workflow import _week_nav, _week_range
from core.ai import research_deep
from core.helpers import H, chip, esc
from core.state import current_week, normalize_deep

_FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
_HEAD = re.compile(r"(?m)^## ")


def split_scenario(text):
    """متن را به (بخش‌های ۱ تا ۸ و منابع، نریشن) تقسیم می‌کند. نریشن همان بخش «متن کامل نریشن» است."""
    body, sep, sources = text.partition("\n\n---\n")
    parts = _HEAD.split(body)
    pre, secs = parts[0], ["## " + p for p in parts[1:]]
    narr, rest = "", []
    for sec in secs:
        first = sec.split("\n", 1)[0]
        if "نریشن" in first and not narr:
            narr = sec.split("\n", 1)[1].strip() if "\n" in sec else ""
        else:
            rest.append(sec.strip())
    kept = (pre.strip() + "\n\n" if pre.strip() else "") + "\n\n".join(rest)
    return kept.strip() + (sep + sources if sep else ""), narr


def compose_view(topic):
    """ترتیب نمایش: ۱) قلاب، ۲) متن کامل نریشن، سپس بقیهٔ بخش‌ها؛ شماره‌ها پشت‌سرهم می‌شوند."""
    body, sep, sources = topic["scenario"].partition("\n\n---\n")
    parts = _HEAD.split(body)
    pre, secs = parts[0].strip(), [p.strip() for p in parts[1:]]
    narr = (topic.get("narration") or "").strip()
    blocks = secs[:1]
    if narr:
        blocks.append("## متن کامل نریشن\n" + narr)
    blocks += secs[1:]
    out = []
    for n, b in enumerate(blocks, 1):
        b = b if b.startswith("## ") else "## " + b
        title = re.sub(r"^[۰-۹0-9]+\) *", "", b.split("\n", 1)[0][3:].strip())
        num = "".join(_FA_DIGITS[int(c)] for c in str(n))
        out.append(f"## {num}) {title}\n" + (b.split("\n", 1)[1] if "\n" in b else ""))
    text = ((pre + "\n\n") if pre else "") + "\n\n".join(out)
    return text + (sep + sources if sep else "")


def render_ideas():
    ss = st.session_state
    normalize_deep()
    with st.container(border=True):
        H('<div class="card-title">ایده‌های موضوعات دیپ‌دایو</div>')
        week, _off = _week_nav(_week_range, prefix="deep_")
        pub = st.date_input("تاریخ انتشار پیشنهادی",
                            value=dt.date.today() + dt.timedelta(days=3), key="pub_date")
        shown = [i for i, t in enumerate(ss.deep_topics) if t.get("week") == week]
        if not shown:
            st.caption("موضوعی برای این هفته نیست.")
        for idx in shown:
            topic = ss.deep_topics[idx]
            with st.container(border=True):
                H(f'<div class="news-title">{esc(topic["title"])} {chip(topic["status"])}</div>')
                with st.container(key=f"keep_idea_{idx}"):
                    b_cal, b_scn = st.columns(2)
                    add_cal = b_cal.button(":material/calendar_month: تقویم", key=f"cal_{idx}")
                    add_scn = b_scn.button(":material/movie: سناریو", key=f"scn_{idx}")
                if add_cal:
                    ss.events = [e for e in ss.events if e["title"] != topic["title"]]
                    ss.events.append({"date": pub.isoformat(), "title": topic["title"]})
                    topic["status"] = "Approved"
                    ss.cal_year, ss.cal_month = pub.year, pub.month
                    st.rerun()
                if add_scn:
                    text = research_deep(topic["title"])
                    if text:
                        topic["scenario"], topic["narration"] = split_scenario(text)
                        ss.pop(f"scn_edit_{idx}", None)   # کادر ویرایش با متن تازه پر شود
                        st.rerun()
                if topic["scenario"]:
                    with st.expander("سناریو و تحقیق دیپ‌دایو", expanded=False):
                        view, edit = st.tabs([":material/visibility: نمایش", ":material/edit: ویرایش نریشن"])
                        with view:
                            st.markdown(compose_view(topic))
                        with edit:
                            edited = st.text_area("متن کامل نریشن", value=topic.get("narration", ""),
                                                  height=420, key=f"scn_edit_{idx}")
                            if st.button(":material/save: ذخیره نریشن", key=f"scn_save_{idx}"):
                                topic["narration"] = edited
                                st.toast("ذخیره شد")
                                st.rerun()
