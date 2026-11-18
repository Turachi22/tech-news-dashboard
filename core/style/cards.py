"""CSS — کارت‌ها، دکمه‌ها، تأیید/رد، عنوان‌ها و کلید هفته."""
CSS_CARDS = """
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

"""
