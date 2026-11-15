import calendar
import copy
import datetime as dt
import html
import time

from google import genai
from google.genai import types
import streamlit as st

st.set_page_config(
    page_title="داشبورد تولید محتوای تکنولوژی",
    layout="wide",
    page_icon="🚀",
)

# ---------------------------------------------------------------------------
# استایل (CSS) — راست‌چین، تیره، کارت‌های شیشه‌ای، سایدبار آیکونی
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;600;800&display=swap');

html, body, .stApp, .stApp p, .stApp label, .stApp button, .stApp input,
.stApp textarea, .stApp h1, .stApp h2, .stApp h3,
.stApp div[data-testid="stMarkdownContainer"] {
    font-family: 'Vazirmatn', 'Tahoma', sans-serif;
}
.stApp {
    background: radial-gradient(circle at 25% 0%, #2b1a63 0%, #14122e 45%, #0a0c1c 100%);
    color: #e5e7eb;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1250px; }

/* راست‌چین */
[data-testid="stMain"], .main { direction: rtl; text-align: right; }
[data-testid="stHorizontalBlock"] { direction: rtl; }
input, textarea { direction: rtl; text-align: right; }
.stApp { overflow-x: hidden; }

/* سایدبار */
[data-testid="stSidebar"] {
    background: #0d1020;
    border-left: 1px solid rgba(255,255,255,.08);
    border-right: none;
    direction: rtl;
}
@media (min-width: 768px) {
    [data-testid="stAppViewContainer"] { flex-direction: row-reverse; }
    [data-testid="stSidebar"] {
        width: 165px !important; min-width: 165px !important; max-width: 165px !important;
    }
}
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%;
    padding: 12px 8px;
    border-radius: 12px;
    border: 1px solid transparent;
    justify-content: center;
    cursor: pointer;
}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-of-type { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(255,255,255,.05); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: rgba(139,92,246,.18);
    border-color: rgba(139,92,246,.55);
}
.brand {
    text-align: center; font-weight: 800; font-size: 1.6rem;
    color: #fff; margin: 6px 0 14px; letter-spacing: 1px;
}

/* کارت‌ها */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.035);
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 16px;
}

/* دکمه‌ها */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.15);
    background: rgba(255,255,255,.05);
    color: #e5e7eb;
    font-weight: 600;
    padding: .4rem .8rem;
}
.stButton > button:hover { border-color: #8b5cf6; color: #fff; }
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border: none; color: #fff;
}
[class*="st-key-rej_"] button { border-color: rgba(239,68,68,.55); color: #fca5a5; }

/* عنوان‌ها */
.page-title { font-size: 1.9rem; font-weight: 800; text-align: center; color: #fff; }
.page-sub { text-align: center; color: #a5b4fc; margin: 4px 0 22px; }
.card-title { font-size: 1.05rem; font-weight: 700; color: #fff; margin-bottom: 10px; }

/* جریان کاری */
.progress { height: 9px; border-radius: 99px; background: rgba(255,255,255,.1); overflow: hidden; margin: 6px 0 4px; }
.progress > div { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #6366f1, #a855f7); }
.muted { color: #94a3b8; font-size: .8rem; }
.stepper { display: flex; align-items: center; gap: 8px; margin: 12px 0 16px; }
.step {
    flex: 1; text-align: center; padding: 9px 6px; border-radius: 10px; font-size: .85rem;
    border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.04);
}
.step b { margin-right: 6px; }
.step.review { border-color: #6366f1; background: rgba(99,102,241,.16); }
.step.done { border-color: #22c55e; background: rgba(34,197,94,.14); }
.arrow { color: #94a3b8; }

.news-title { font-weight: 700; color: #fff; }
.news-desc { color: #cbd5e1; font-size: .88rem; margin-top: 4px; }
.avatar {
    width: 64px; height: 64px; border-radius: 14px; font-size: 2rem;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #312e81, #6d28d9);
}
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div {
    background: rgba(255,255,255,.06) !important;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input, textarea {
    color: #fff !important; -webkit-text-fill-color: #fff;
}
.chip { display: inline-block; white-space: nowrap; font-size: .7rem; padding: 2px 8px; border-radius: 99px; margin-right: 6px; font-weight: 600; }
.chip-pending { background: rgba(148,163,184,.2); color: #cbd5e1; }
.chip-review { background: rgba(99,102,241,.25); color: #c7d2fe; }
.chip-done { background: rgba(34,197,94,.2); color: #86efac; }
.chip-rej { background: rgba(239,68,68,.2); color: #fca5a5; }

/* آمار */
.stats-wrap { display: flex; gap: 22px; align-items: center; flex-wrap: wrap; }
.bars { flex: 1; min-width: 200px; }
.bar-area { height: 130px; display: flex; align-items: flex-end; gap: 10px; }
.bar { flex: 1; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, #a855f7, #6366f1); }
.bar-labels { display: flex; gap: 10px; margin-top: 4px; }
.bar-labels span { flex: 1; text-align: center; color: #94a3b8; font-size: .75rem; }
.donut { width: 125px; height: 125px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.donut-in {
    width: 78px; height: 78px; border-radius: 50%; background: #15152e;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.donut-in b { font-size: 1.3rem; color: #fff; }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 16px; }
.tile { background: rgba(255,255,255,.05); border-radius: 12px; padding: 10px 4px; text-align: center; }
.tile b { display: block; font-size: 1.2rem; color: #fff; }
.tile small { color: #94a3b8; }

/* تقویم */
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; direction: rtl; }
.wd { color: #94a3b8; font-size: .78rem; padding: 4px 0; }
.cell { padding: 7px 0; border-radius: 8px; font-size: .85rem; position: relative; }
.cell.today { background: #6366f1; color: #fff; }
.cell.has { background: rgba(168,85,247,.28); }
.cell i {
    position: absolute; bottom: 3px; left: 50%; width: 5px; height: 5px;
    margin-left: -2px; border-radius: 50%; background: #f0abfc;
}

/* چیدمان کلی: ستون اول سمت چپ؛ در موبایل زیر هم و به همین ترتیب */
[class*="st-key-layout"] [data-testid="stHorizontalBlock"] { direction: ltr; }
[class*="st-key-layout"] [data-testid="stColumn"],
[class*="st-key-layout"] [data-testid="column"] { direction: rtl; }
[class*="st-key-layout"] [data-testid="stColumn"] [data-testid="stHorizontalBlock"],
[class*="st-key-layout"] [data-testid="column"] [data-testid="stHorizontalBlock"] { direction: rtl; }

/* ردیف‌های دکمه: در موبایل هم کنار هم بمانند */
[class*="st-key-keep"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .4rem; }
[class*="st-key-keep"] [data-testid="stColumn"],
[class*="st-key-keep"] [data-testid="column"] {
    min-width: 0 !important; width: auto !important; flex: 1 1 0 !important;
}

.news-head { display: flex; gap: 12px; align-items: center; }
.news-head .avatar { flex: 0 0 auto; }

@media (max-width: 640px) {
    .block-container { padding: 1rem .7rem 3rem; }
    .page-title { font-size: 1.35rem; }
    .page-sub { font-size: .85rem; margin-bottom: 14px; }
    .avatar { width: 48px; height: 48px; font-size: 1.5rem; border-radius: 12px; }
    .stepper { gap: 4px; }
    .step { font-size: .72rem; padding: 7px 2px; }
    .step b { display: block; margin: 0; font-size: .95rem; }
    .tiles { grid-template-columns: repeat(2, 1fr); }
    .donut { margin: 0 auto; }
    .stButton > button { font-size: .8rem; padding: .35rem .2rem; }
    .cell { padding: 5px 0; font-size: .78rem; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------------------------
FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
MONTHS_FA = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
             "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]
WEEKDAYS_FA = ["ش", "ی", "د", "س", "چ", "پ", "ج"]  # هفته از شنبه
STATUS_FA = {"Pending": "در صف", "Reviewing": "در حال بررسی",
             "Approved": "تأیید شده", "Rejected": "رد شده"}
STATUS_CHIP = {"Pending": "chip-pending", "Reviewing": "chip-review",
               "Approved": "chip-done", "Rejected": "chip-rej"}
PAGES = ["🏠 خانه", "📰 اخبار", "💡 دیپ‌دایو", "📊 آمار", "⚙️ تنظیمات"]


def fa(value):
    if isinstance(value, int):
        value = f"{value:,}".replace(",", "٬")
    return str(value).translate(FA_DIGITS)


def esc(text):
    return html.escape(str(text))


def H(markup):
    st.markdown(markup, unsafe_allow_html=True)


def chip(status):
    return f'<span class="chip {STATUS_CHIP[status]}">{STATUS_FA[status]}</span>'


NEWS_DEFAULT = [
    {"title": "ربات‌های انسان‌نما با یادگیری شهودی",
     "desc": "قابلیت یادگیری کارهای خانه با مشاهدهٔ رفتار انسان.",
     "icon": "🤖", "status": "Pending", "ai": ""},
    {"title": "سیگنال‌های مرموز فضایی",
     "desc": "کشف امواج رادیویی ناشناخته از لبهٔ منظومهٔ شمسی.",
     "icon": "📡", "status": "Pending", "ai": ""},
    {"title": "بافت‌های زیستی چاپ‌شده سه‌بعدی",
     "desc": "ترمیم خودکار آسیب‌های بافتی داخل بدن.",
     "icon": "🧬", "status": "Pending", "ai": ""},
]
DEEP_DEFAULT = [
    {"title": "رازهای پنهان الگوریتم‌های کلود شانون", "status": "Pending", "scenario": ""},
    {"title": "تکنولوژی فراموش‌شدهٔ باتری‌های حالت جامد", "status": "Pending", "scenario": ""},
    {"title": "پشت پردهٔ پروژه‌های محرمانهٔ فضایی مهار انرژی خورشیدی", "status": "Pending", "scenario": ""},
]


def init_state():
    ss = st.session_state
    today = dt.date.today()
    ss.setdefault("news_list", copy.deepcopy(NEWS_DEFAULT))
    ss.setdefault("deep_topics", copy.deepcopy(DEEP_DEFAULT))
    ss.setdefault("events", [])
    ss.setdefault("cal_year", today.year)
    ss.setdefault("cal_month", today.month)
    ss.setdefault("views", [120, 250, 180, 300, 450, 380, 520])
    ss.setdefault("total_views", 12424)


init_state()


# ---------------------------------------------------------------------------
# هوش مصنوعی (Gemini)
# ---------------------------------------------------------------------------
RESEARCH_RULES = (
    "تو دستیار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و پاسخ را به زبان فارسی، "
    "کامل، دقیق و با جزئیات بنویس (محدودیتی برای طول نیست). اعداد، تاریخ‌ها، نام افراد و شرکت‌ها را بیاور. "
    "هر ادعای مهم را با نام منبع همراه کن. هرگز خودت لینک نساز؛ لینک منابع واقعی بعد از متن "
    "به‌صورت خودکار اضافه می‌شود. اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)
NEWS_PROMPT = RESEARCH_RULES + (
    "ساختار پاسخ: ۱) توضیح ساده برای مخاطب عمومی (سطح کلاس ششم)؛ ۲) جزئیات فنی و آمار؛ "
    "۳) پیشینه و زمینهٔ خبر؛ ۴) محدودیت‌ها، مناقشه‌ها و میزان اطمینان به درستی خبر؛ "
    "۵) چند زاویهٔ پیشنهادی برای ویدیو.\nخبر: {title} — {desc}"
)
DEEP_PROMPT = RESEARCH_RULES + (
    "برای یک مینی‌مستند تکنولوژی دربارهٔ موضوع زیر اطلاعات پس‌زمینه، تاریخچه، حقایق کلیدی، "
    "نکته‌های کمتر شناخته‌شده و چند زاویهٔ روایی جذاب ارائه بده.\nموضوع: {title}"
)


def _auto_model(client):
    """مناسب‌ترین مدل flash را از فهرست مدل‌های حساب شما پیدا می‌کند."""
    names = [m.name for m in client.models.list()
             if "generateContent" in (getattr(m, "supported_actions", None) or [])]
    skip = ("image", "tts", "live", "embedding", "audio", "exp", "vision", "robotics", "gemma", "lite")
    flash = sorted((n for n in names if "flash" in n and not any(x in n for x in skip)), reverse=True)
    return (flash or names or [None])[0]


def _stream(client, model_name, prompt, box, use_search=True):
    cfg = types.GenerateContentConfig(
        temperature=0.4,
        tools=[types.Tool(google_search=types.GoogleSearch())] if use_search else None,
    )
    text, sources = "", {}
    for chunk in client.models.generate_content_stream(model=model_name, contents=prompt, config=cfg):
        text += chunk.text or ""
        try:
            for gc in chunk.candidates[0].grounding_metadata.grounding_chunks or []:
                if gc.web and gc.web.uri:
                    sources.setdefault(gc.web.uri, gc.web.title or gc.web.uri)
        except (AttributeError, IndexError, TypeError):
            pass
        box.markdown(text + " ▌")
    if sources:
        text += "\n\n---\n**منابع (لینک‌های واقعی از جست‌وجوی گوگل):**\n" + "\n".join(
            f"{i}. [{title}]({uri})" for i, (uri, title) in enumerate(sources.items(), 1))
    elif use_search:
        text += "\n\n---\n⚠️ این بار جست‌وجو لینکی برنگرداند؛ اطلاعات را پیش از انتشار راستی‌آزمایی کنید."
    box.markdown(text)
    return text


def ask_ai(prompt, box=None):
    """پاسخ را زنده نشان می‌دهد و متن کامل (همراه لینک منابع واقعی) را برمی‌گرداند."""
    ss = st.session_state
    key = ss.get("api_key", "")
    if not key:
        st.error("لطفاً کلید Gemini را در منوی کناری وارد کنید.")
        return None
    box = box if box is not None else st.empty()
    client = genai.Client(api_key=key)
    name = (ss.get("model_name") or "").strip() or ss.get("auto_model") or "gemini-flash-latest"
    text, err = None, None
    try:
        text = _stream(client, name, prompt, box)
    except Exception as exc:  # noqa: BLE001
        err = exc
        msg = str(exc).lower()
        try:
            if any(w in msg for w in ("404", "no longer available", "not found", "not supported")):
                auto = _auto_model(client)
                if auto and auto.replace("models/", "") != name.replace("models/", ""):
                    ss["auto_model"] = auto
                    st.info(f"مدل «{name}» در دسترس نبود؛ با «{auto}» انجام شد.")
                    text, err = _stream(client, auto, prompt, box), None
            elif any(w in msg for w in ("google_search", "grounding", "tool")):
                st.warning("جست‌وجوی وب برای این کلید/مدل فعال نیست؛ پاسخ بدون لینک منبع تولید شد.")
                text, err = _stream(client, name, prompt, box, use_search=False), None
        except Exception as exc2:  # noqa: BLE001
            err = exc2
    if text is None:
        st.error(f"خطا در ارتباط با Gemini: {err}")
        return None
    if not text.strip():
        st.error("پاسخی دریافت نشد. نام مدل را در منوی کناری عوض کنید.")
        return None
    return text


# ---------------------------------------------------------------------------
# اجزای رابط
# ---------------------------------------------------------------------------
def header(title, sub):
    H(f'<div class="page-title">{title}</div><div class="page-sub">{sub}</div>')


def news_item(idx, item):
    with st.container(border=True):
        H('<div class="news-head">'
          f'<div class="avatar">{item["icon"]}</div>'
          f'<div><div class="news-title">{esc(item["title"])} {chip(item["status"])}</div>'
          f'<div class="news-desc">{esc(item["desc"])}</div></div></div>')

        with st.container(key=f"keep_news_{idx}"):
            b_ok, b_no, b_ai = st.columns(3)
            ok = b_ok.button("➕ تأیید", key=f"app_{idx}", type="primary")
            no = b_no.button("✖ رد", key=f"rej_{idx}")
            ai = b_ai.button("🔍 بررسی", key=f"rev_{idx}")
        if ok:
            item["status"] = "Approved"
            st.rerun()
        if no:
            item["status"] = "Rejected"
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


def render_workflow():
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
            news_item(idx, item)


def render_ideas():
    ss = st.session_state
    with st.container(border=True):
        H('<div class="card-title">ایده‌های موضوعات دیپ‌دایو</div>')
        pub = st.date_input("تاریخ انتشار پیشنهادی",
                            value=dt.date.today() + dt.timedelta(days=3), key="pub_date")
        for idx, topic in enumerate(ss.deep_topics):
            with st.container(border=True):
                H(f'<div class="news-title">{esc(topic["title"])} {chip(topic["status"])}</div>')
                with st.container(key=f"keep_idea_{idx}"):
                    b_cal, b_scn = st.columns(2)
                    add_cal = b_cal.button("📅 تقویم", key=f"cal_{idx}")
                    add_scn = b_scn.button("🎬 سناریو", key=f"scn_{idx}")
                if add_cal:
                    ss.events = [e for e in ss.events if e["title"] != topic["title"]]
                    ss.events.append({"date": pub.isoformat(), "title": topic["title"]})
                    topic["status"] = "Approved"
                    ss.cal_year, ss.cal_month = pub.year, pub.month
                    st.rerun()
                if add_scn:
                    text = ask_ai(DEEP_PROMPT.format(title=topic["title"]))
                    if text:
                        topic["scenario"] = text
                        st.rerun()
                if topic["scenario"]:
                    with st.expander("سناریو و زوایای روایت"):
                        st.markdown(topic["scenario"])


def render_stats():
    ss = st.session_state
    news = ss.news_list
    counts = {s: sum(1 for n in news if n["status"] == s) for s in STATUS_FA}
    total = len(news)

    top = max(ss.views) or 1
    bars = "".join(
        f'<div class="bar" title="{fa(v)}" style="height:{max(6, round(v / top * 100))}%"></div>'
        for v in ss.views)
    labels = "".join(f"<span>{d}</span>" for d in WEEKDAYS_FA[: len(ss.views)])

    colors = {"Approved": "#22c55e", "Reviewing": "#6366f1", "Pending": "#a855f7", "Rejected": "#ef4444"}
    parts, cum = [], 0
    for status, color in colors.items():
        if counts[status]:
            start = cum / total * 100
            cum += counts[status]
            parts.append(f"{color} {start:.1f}% {cum / total * 100:.1f}%")
    gradient = ", ".join(parts) if parts else "#334155 0% 100%"

    queued = counts["Pending"] + counts["Reviewing"]
    with st.container(border=True):
        H('<div class="card-title">آمارهای کلیدی تولید محتوا</div>')
        H('<div class="stats-wrap">'
          f'<div class="bars"><div class="bar-area">{bars}</div><div class="bar-labels">{labels}</div></div>'
          f'<div class="donut" style="background:conic-gradient({gradient})">'
          f'<div class="donut-in"><b>{fa(total)}</b><small class="muted">خبر</small></div></div>'
          '</div>'
          '<div class="tiles">'
          f'<div class="tile"><b>{fa(ss.total_views)}</b><small>بازدید کل</small></div>'
          f'<div class="tile"><b>{fa(queued)}</b><small>در صف</small></div>'
          f'<div class="tile"><b>{fa(counts["Approved"])}</b><small>تأیید شده</small></div>'
          f'<div class="tile"><b>{fa(counts["Rejected"])}</b><small>رد شده</small></div>'
          '</div>')


def render_calendar():
    ss = st.session_state
    y, m = ss.cal_year, ss.cal_month
    today_iso = dt.date.today().isoformat()
    with st.container(border=True):
        H('<div class="card-title">تقویم محتوا</div>')
        with st.container(key="keep_cal_nav"):
            c_prev, c_mid, c_next = st.columns(3)
            prev = c_prev.button("→", key="cal_prev")
            c_mid.markdown(f'<div style="text-align:center;font-weight:700;padding-top:.4rem">'
                           f'{MONTHS_FA[m - 1]} {fa(y)}</div>', unsafe_allow_html=True)
            nxt = c_next.button("←", key="cal_next")
        if prev:
            ss.cal_year, ss.cal_month = (y - 1, 12) if m == 1 else (y, m - 1)
            st.rerun()
        if nxt:
            ss.cal_year, ss.cal_month = (y + 1, 1) if m == 12 else (y, m + 1)
            st.rerun()

        cells = []
        for week in calendar.Calendar(firstweekday=5).monthdayscalendar(y, m):
            for d in week:
                if d == 0:
                    cells.append('<div class="cell"></div>')
                    continue
                iso = f"{y:04d}-{m:02d}-{d:02d}"
                evs = [e for e in ss.events if e["date"] == iso]
                cls = "cell" + (" today" if iso == today_iso else "") + (" has" if evs else "")
                tip = esc(" | ".join(e["title"] for e in evs))
                cells.append(f'<div class="{cls}" title="{tip}">{fa(d)}{"<i></i>" if evs else ""}</div>')
        head = "".join(f'<div class="wd">{d}</div>' for d in WEEKDAYS_FA)
        H(f'<div class="cal-grid">{head}{"".join(cells)}</div>')

        month_prefix = f"{y:04d}-{m:02d}"
        month_events = [e for e in ss.events if e["date"].startswith(month_prefix)]
        for i, ev in enumerate(sorted(month_events, key=lambda e: e["date"])):
            if st.button(f"🗑 {fa(ev['date'])} — {ev['title']}", key=f"del_{i}"):
                ss.events.remove(ev)
                st.rerun()


# ---------------------------------------------------------------------------
# سایدبار
# ---------------------------------------------------------------------------
with st.sidebar:
    H('<div class="brand">ساده</div>')
    st.radio("منو", PAGES, key="page", label_visibility="collapsed")
    st.markdown("---")
    with st.expander("🔑 Gemini"):
        st.text_input("کلید API", type="password", key="api_key")
        st.text_input("نام مدل (اختیاری)", key="model_name", placeholder="خالی = انتخاب خودکار")

page = st.session_state.page

# ---------------------------------------------------------------------------
# صفحه‌ها
# ---------------------------------------------------------------------------
if page == PAGES[0]:
    header("داشبورد شخصی تولید محتوای تکنولوژی 🚀",
           "مدیریت هوشمند اخبار هفتگی و بخش دوم (دیپ‌دایو)")
    with st.container(key="layout_top"):
        col_flow, col_ideas = st.columns([2, 1], gap="medium")  # ستون اول = سمت چپ (و در موبایل بالاتر)
        with col_flow:
            render_workflow()
        with col_ideas:
            render_ideas()
    with st.container(key="layout_bottom"):
        col_stats, col_cal = st.columns([1.6, 1], gap="medium")
        with col_stats:
            render_stats()
        with col_cal:
            render_calendar()

elif page == PAGES[1]:
    header("اخبار داغ هفته", "بررسی، تأیید یا ردِ خبرهای پیشنهادی")
    render_workflow()
    with st.form("add_news", clear_on_submit=True):
        t = st.text_input("عنوان خبر جدید")
        d = st.text_input("توضیح کوتاه")
        if st.form_submit_button("افزودن خبر") and t.strip():
            st.session_state.news_list.append(
                {"title": t.strip(), "desc": d.strip(), "icon": "📰", "status": "Pending", "ai": ""})
            st.rerun()

elif page == PAGES[2]:
    header("موضوعات دیپ‌دایو", "ایده‌های عمیق و مینی‌مستند")
    render_ideas()
    with st.form("add_topic", clear_on_submit=True):
        t = st.text_input("موضوع جدید")
        if st.form_submit_button("افزودن موضوع") and t.strip():
            st.session_state.deep_topics.append({"title": t.strip(), "status": "Pending", "scenario": ""})
            st.rerun()
    render_calendar()

elif page == PAGES[3]:
    header("آمار و تحلیل", "نمای کلی عملکرد محتوا")
    render_stats()

else:
    header("تنظیمات", "تنظیمات داشبورد")
    with st.container(border=True):
        st.text_input("نام کانال یوتیوب", value="کانال ساده")
        st.selectbox("وضعیت بروزرسانی خودکار", ["فعال", "غیرفعال"])
        if st.button("بازنشانی همهٔ داده‌ها"):
            for k in ("news_list", "deep_topics", "events"):
                st.session_state.pop(k, None)
            st.rerun()
