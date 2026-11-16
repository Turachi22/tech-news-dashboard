"""کارت «آمارهای کلیدی» (نمودار ستونی، دونات، کاشی‌های عددی)."""
import streamlit as st

from core.helpers import STATUS_FA, WEEKDAYS_FA, H, fa


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
