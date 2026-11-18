"""CSS — تم: رنگ‌ها (متغیرهای :root)، فونت، راست‌چین، سایدبار و منوی کناری."""
CSS_BASE = """
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

"""
