"""ظاهر برنامه (CSS) — تم «شیشه‌ای تیره، فیروزه‌ای». برای تغییر رنگ/فونت/فاصله‌ها فقط همین فایل را ویرایش کنید.
رنگ‌ها در متغیرهای بالای :root هستند؛ با عوض‌کردن --accent رنگ اصلی کل برنامه عوض می‌شود."""
import streamlit as st
import streamlit.components.v1 as components

FONT_URL = "https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap"

CSS = """
<style>
@import url('__FONT__');

:root {
    --bg:#060a14; --panel:rgba(255,255,255,.035); --card:rgba(255,255,255,.05); --card2:rgba(255,255,255,.06);
    --line:rgba(255,255,255,.10); --text:#f1f5ff; --muted:#93a0ba; --faint:#5e6a84;
    --accent:#2dd4bf; --accent2:#38bdf8; --accent-soft:rgba(45,212,191,.13); --accent-ink:#5eead4; --on-accent:#04201c;
    --ok:#34d399; --ok-soft:rgba(52,211,153,.13); --bad:#fb7185; --bad-soft:rgba(251,113,133,.13);
    --warn:#fbbf24; --warn-soft:rgba(251,191,36,.13);
    --r:20px; --rs:12px; --shadow:0 12px 40px rgba(0,0,0,.35);
    --grad:linear-gradient(90deg,#2dd4bf,#38bdf8);
}

/* فونت: وزیرمتن روی همه‌چیز (به‌جز آیکن‌ها و کد) */
html, body, .stApp,
.stApp *:not([data-testid="stIconMaterial"]):not([class*="material-symbols"]):not(.material-icons) {
    font-family: 'Vazirmatn', 'Tahoma', sans-serif;
}
.stApp code, .stApp pre, .stApp pre * { font-family: ui-monospace, Menlo, Consolas, monospace !important; }
.stApp {
    background-color: var(--bg);
    background-image: radial-gradient(800px 480px at 90% -10%, rgba(45,212,191,.16), transparent 60%),
                      radial-gradient(700px 520px at -5% 105%, rgba(56,189,248,.16), transparent 60%);
    background-attachment: fixed;
    color: var(--text);
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; max-width: 1250px; }
h1, h2, h3 { letter-spacing: -.2px; }

/* راست‌چین */
[data-testid="stMain"], .main { direction: rtl; text-align: right; }
[data-testid="stHorizontalBlock"] { direction: rtl; }
input, textarea { direction: rtl; text-align: right; }
.stApp { overflow-x: hidden; }

/* سایدبار */
[data-testid="stSidebar"] {
    background: rgba(8,12,24,.72);
    -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
    border-left: 1px solid var(--line);
    border-right: none;
    direction: rtl;
}
@media (min-width: 768px) {
    [data-testid="stAppViewContainer"] { flex-direction: row-reverse; }
    [data-testid="stSidebar"] {
        width: 232px !important; min-width: 232px !important; max-width: 232px !important;
    }
}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

/* منوی کناری: آیکن + متن، گزینهٔ فعال با نوار رنگی */
[class*="st-key-nav_"] button {
    justify-content: flex-start; text-align: right; gap: .7rem;
    background: transparent !important; border: none !important; box-shadow: none !important;
    color: var(--muted) !important; font-weight: 500; padding: .6rem .8rem; border-radius: var(--rs);
}
[class*="st-key-nav_"] button:hover { background: rgba(255,255,255,.05) !important; color: var(--text) !important; }
[class*="st-key-nav_"] button[kind="primary"],
[class*="st-key-nav_"] button[data-testid="stBaseButton-primary"] {
    background: var(--accent-soft) !important; color: var(--accent-ink) !important; font-weight: 700;
    box-shadow: inset -3px 0 0 var(--accent) !important;
}
[class*="st-key-nav_"] button p { margin: 0; }

.brand { text-align: center; margin: 2px 0 12px; }

/* کارت‌ها */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--line) !important;
    border-radius: var(--r);
    box-shadow: var(--shadow);
    -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
}
[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlockBorderWrapper"] {
    box-shadow: none; background: var(--card2); border-radius: var(--rs);
}

/* دکمه‌ها */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
    width: 100%;
    border-radius: var(--rs);
    border: 1px solid var(--line);
    background: transparent;
    color: var(--text);
    font-weight: 600;
    padding: .45rem .9rem;
    transition: border-color .15s, background .15s, transform .05s;
}
.stButton > button p, .stDownloadButton > button p { margin: 0; }
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--accent); color: var(--accent-ink); background: var(--accent-soft);
}
.stButton > button:active { transform: scale(.98); }
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] {
    background: var(--grad); border: none; color: var(--on-accent); font-weight: 700;
}
.stButton > button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
    filter: brightness(1.08); color: var(--on-accent); background: var(--grad);
}
.stButton > button:disabled { opacity: .35; }
/* تأیید / رد: رنگ معنایی */
[class*="st-key-app_"] button {
    background: var(--ok-soft) !important; color: var(--ok) !important; border-color: transparent !important;
}
[class*="st-key-rej_"] button {
    background: var(--bad-soft) !important; color: var(--bad) !important; border-color: transparent !important;
}

/* عنوان‌ها */
.page-head { margin: 0 0 18px; }
.page-title { font-size: 1.7rem; font-weight: 800; color: var(--text); }
.page-sub { color: var(--muted); margin-top: 4px; font-size: .88rem; }
.card-title { font-size: 1.05rem; font-weight: 700; color: var(--text); margin-bottom: 10px; }
.muted { color: var(--muted); font-size: .8rem; }
.ico-svg { vertical-align: -3px; flex: none; }

/* هفته‌نما */
[class*="st-key-keep_weeknav"] {
    background: rgba(255,255,255,.06); border: 1px solid var(--line); border-radius: 999px;
    padding: 4px; margin-bottom: 14px;
}
[class*="st-key-keep_weeknav"] .stButton > button {
    border: none; border-radius: 999px; color: var(--muted); background: transparent; font-weight: 500;
}
.wk-mid { text-align: center; line-height: 1.35; padding: .15rem 0; }
.wk-mid b { display: block; font-size: .88rem; }
.wk-mid span { color: var(--muted); font-size: .72rem; }

/* جریان کاری */
.sum-row { display: flex; align-items: center; gap: 18px; margin: 6px 0 14px; }
.sum-t { font-weight: 700; font-size: .98rem; }
.progress { flex: 1; max-width: 280px; height: 5px; border-radius: 99px; background: var(--line); overflow: hidden; }
.progress > div { height: 100%; border-radius: 99px; background: var(--grad); }
.day-label { display: flex; align-items: center; gap: 7px; color: var(--muted); font-size: .8rem; margin: 14px 0 8px; }

/* دسته‌بندی خبرها (کنترل قرصی) */
[class*="st-key-news_tab"] { margin-bottom: 6px; }
[class*="st-key-news_tab"] button { border-radius: 10px; font-weight: 600; }

/* کارت خبر */
[class*="st-key-newscard_"] {
    position: relative; background: var(--card2); border: 1px solid var(--line);
    border-radius: var(--r); padding: 16px 18px 14px; gap: .7rem; margin-bottom: 4px;
}
[class*="st-key-newscard_"]::before {
    content: ""; position: absolute; right: 0; top: 16px; bottom: 16px; width: 3px;
    border-radius: 3px; background: var(--faint);
}
[class*="st-key-newscard_"][class*="_Reviewing"]::before { background: var(--warn); }
[class*="st-key-newscard_"][class*="_Approved"]::before { background: var(--ok); }
[class*="st-key-newscard_"][class*="_Rejected"]::before { background: var(--bad); }
.news-head { display: flex; gap: 14px; align-items: flex-start; }
.news-title { font-weight: 700; font-size: 1rem; color: var(--text); line-height: 1.8; }
.news-desc { color: var(--muted); font-size: .88rem; margin-top: 4px; line-height: 1.9; }
.avatar {
    width: 42px; height: 42px; border-radius: 12px; flex: 0 0 auto;
    display: flex; align-items: center; justify-content: center;
    background: var(--accent-soft); color: var(--accent-ink);
}

/* ورودی‌ها و بازشوها */
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="select"] > div, textarea {
    background: rgba(255,255,255,.05) !important; border-radius: var(--rs) !important;
}
[data-baseweb="input"] input, [data-baseweb="base-input"] input, textarea {
    color: var(--text) !important; -webkit-text-fill-color: var(--text);
}
[data-testid="stExpander"] details {
    background: rgba(255,255,255,.035); border: 1px solid var(--line) !important; border-radius: var(--rs);
}
[data-testid="stExpander"] summary { font-weight: 600; color: var(--muted); }
[data-testid="stAlert"] { border-radius: var(--rs); }

/* برچسب وضعیت */
.chip { display: inline-block; white-space: nowrap; font-size: .7rem; padding: 2px 10px; border-radius: 99px;
        margin-right: 8px; font-weight: 600; vertical-align: middle; }
.chip-pending { background: rgba(255,255,255,.07); color: var(--muted); border: 1px solid var(--line); }
.chip-review { background: var(--warn-soft); color: var(--warn); }
.chip-done { background: var(--ok-soft); color: var(--ok); }
.chip-rej { background: var(--bad-soft); color: var(--bad); }

/* نشانگر سهمیه (سایدبار) */
.qbox { border: 1px solid var(--line); border-radius: var(--r); padding: 12px 14px; margin: 14px 0 10px;
        background: var(--card); font-size: .8rem; direction: rtl; }
.q-head { display: flex; justify-content: space-between; color: var(--muted); }
.q-head b { color: var(--text); }
.q-bar { height: 5px; border-radius: 5px; background: var(--line); margin: 9px 0; overflow: hidden; }
.q-fill { height: 100%; border-radius: 5px; }
.q-fill.ok { background: var(--grad); } .q-fill.warn { background: var(--warn); } .q-fill.bad { background: var(--bad); }
.q-state { color: var(--muted); display: flex; align-items: center; gap: 7px; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot.ok { background: var(--ok); box-shadow: 0 0 0 3px var(--ok-soft); }
.dot.warn { background: var(--warn); box-shadow: 0 0 0 3px var(--warn-soft); }
.q-row { display: flex; flex-direction: column; margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--line); }
.q-row span { color: var(--faint); font-size: .72rem; }

/* آمار */
.stats-wrap { display: flex; gap: 22px; align-items: center; flex-wrap: wrap; }
.bars { flex: 1; min-width: 200px; }
.bar-area { height: 130px; display: flex; align-items: flex-end; gap: 10px; }
.bar { flex: 1; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, #2dd4bf, #38bdf8); opacity: .9; }
.bar-labels { display: flex; gap: 10px; margin-top: 4px; }
.bar-labels span { flex: 1; text-align: center; color: var(--muted); font-size: .75rem; }
.donut { width: 125px; height: 125px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.donut-in {
    width: 82px; height: 82px; border-radius: 50%; background: #0b1220;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.donut-in b { font-size: 1.3rem; color: var(--text); }
.tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 16px; }
.tile { background: rgba(255,255,255,.05); border: 1px solid var(--line); border-radius: var(--rs);
        padding: 12px 4px; text-align: center; }
.tile b { display: block; font-size: 1.2rem; color: var(--text); }
.tile small { color: var(--muted); }

/* تقویم */
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; direction: rtl; }
.wd { color: var(--muted); font-size: .78rem; padding: 4px 0; }
.cell { padding: 7px 0; border-radius: 10px; font-size: .85rem; position: relative; }
.cell.today { background: var(--accent); color: var(--on-accent); font-weight: 700; }
.cell.has { background: var(--accent-soft); }
.cell i {
    position: absolute; bottom: 3px; left: 50%; width: 5px; height: 5px;
    margin-left: -2px; border-radius: 50%; background: var(--accent2);
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

@media (max-width: 640px) {
    .block-container { padding: 1rem .7rem 3rem; }
    .page-title { font-size: 1.35rem; }
    .avatar { width: 38px; height: 38px; }
    [class*="st-key-newscard_"] { padding: 14px 12px 12px; }
    .sum-row { gap: 10px; }
    .tiles { grid-template-columns: repeat(2, 1fr); }
    .donut { margin: 0 auto; }
    .stButton > button { font-size: .8rem; padding: .35rem .2rem; }
    .cell { padding: 5px 0; font-size: .78rem; }
}
</style>
""".replace("__FONT__", FONT_URL)

# اگر @import داخل صفحه اعمال نشد، همین لینک مستقیم به <head> صفحهٔ میزبان اضافه می‌شود
_FONT_JS = """<script>
(function () {
  try {
    var d = window.parent.document;
    if (d.querySelector('link[data-sade-font]')) return;
    var l = d.createElement('link');
    l.rel = 'stylesheet'; l.href = '%s'; l.setAttribute('data-sade-font', '1');
    d.head.appendChild(l);
  } catch (e) {}
})();
</script>""" % FONT_URL


def apply_css():
    st.markdown(CSS, unsafe_allow_html=True)
    components.html(_FONT_JS, height=0)
