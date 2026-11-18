"""ثابت‌های جمع‌آوری خبر (مهلت‌ها، سقف‌ها، تعداد کاندیدها)."""

HN_MIN_POINTS = 60            # حداقل امتیاز Hacker News برای کاندیدشدنِ خبرِ فقط‌HN
TIMEOUT = 8                   # ثانیه برای هر منبع
BUDGET = 28                   # سقف کل زمان جمع‌آوری (ثانیه)
WORKERS = 14
PER_DOMAIN = 6                # بهترین‌های هر حوزه که به Gemini داده می‌شود
GENERAL_TOP = 10
MAX_CANDIDATES = 64
CACHE_SECONDS = 20 * 60

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
