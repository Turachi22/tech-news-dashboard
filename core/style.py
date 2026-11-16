"""ظاهر برنامه (CSS). برای تغییر رنگ/فونت/فاصله‌ها فقط همین فایل را ویرایش کنید."""
import streamlit as st

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


def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)
