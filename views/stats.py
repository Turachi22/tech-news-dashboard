"""صفحهٔ آمار."""
from components.stats_card import render_stats
from core.helpers import header


def render():
    header("آمار و تحلیل", "نمای کلی عملکرد محتوا")
    render_stats()
