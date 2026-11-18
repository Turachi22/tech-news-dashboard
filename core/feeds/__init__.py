"""جمع‌آوری خبر از فیدها. بقیهٔ برنامه فقط از همین‌جا استفاده می‌کند: `from core import feeds`.

- sources.py  فهرست سایت‌ها و جست‌وجوها (برای افزودن/حذف منبع فقط این فایل را ویرایش کنید)
- config.py   مهلت‌ها و سقف‌ها
- fetch.py    دریافت و تجزیهٔ RSS/Atom، Google News، Hacker News
- rank.py     خوشه‌بندی، تشخیص حوزه، امتیازدهی
- collect.py  نقطهٔ ورود: collect / shortlist / format_candidates / health_report
"""
from core.feeds.collect import collect, format_candidates, health_report, shortlist  # noqa: F401
from core.feeds.rank import classify  # noqa: F401
from core.feeds.sources import DOMAIN_FA, FEEDS, NEWS_QUERIES  # noqa: F401
