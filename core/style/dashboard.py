"""CSS — آمار، تقویم، چیدمان کلی و حالت موبایل."""
CSS_DASHBOARD = """
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
"""
