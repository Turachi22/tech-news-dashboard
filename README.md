# داشبورد کانال ساده

هر بخش برنامه یک فایل جدا دارد. موقع اصلاح، فقط همان فایل را عوض کنید؛ بقیه دست‌نخورده می‌مانند.

```
app.py                      ← منو (فهرست ROUTES) و مسیریابی صفحه‌ها
core/
  style.py                  ← ظاهر: رنگ‌ها، فونت، کارت‌ها، موبایل (CSS)
  helpers.py                ← اعداد فارسی، چیپ وضعیت، عنوان صفحه
  state.py                  ← دادهٔ پیش‌فرض، ذخیره/بارگذاری (data.json)
  ai.py                     ← Gemini: مدل‌ها، کلیدها، جست‌وجو، لینک منبع، پرامپت‌ها
  export.py                 ← خروجی Word
components/                 ← کارت‌های قابل‌استفادهٔ مجدد
  sidebar.py                ← منوی کناری و پنل کلیدها
  workflow.py               ← جریان کاری اخبار، تأیید/رد، اسکریپت
  ideas.py                  ← ایده‌های دیپ‌دایو
  stats_card.py             ← آمار
  calendar_card.py          ← تقویم
views/                      ← صفحه‌ها (فقط چیدمان کارت‌ها)
  home.py  news.py  deep.py  stats.py  settings.py
```

## کدام بخش را کجا عوض کنم؟
| می‌خواهم... | فایل |
|---|---|
| گزینه به منو اضافه یا حذف کنم | `app.py` (ROUTES) |
| ظاهر پنل کناری / کلیدها را عوض کنم | `components/sidebar.py` |
| رنگ و فونت و فاصله‌ها را عوض کنم | `core/style.py` |
| چیدمان صفحهٔ خانه را عوض کنم | `views/home.py` |
| کارت اخبار، دکمه‌ها، اسکریپت | `components/workflow.py` |
| صفحهٔ اخبار (فرم افزودن، خروجی کلی) | `views/news.py` |
| پرامپت یا رفتار Gemini | `core/ai.py` |
| قالب فایل Word | `core/export.py` |

## افزودن صفحهٔ جدید
1. فایل `views/report.py` با تابع `render()` بسازید.
2. در `app.py` دو خط اضافه کنید: `import report` در فهرست `from views import ...` و یک سطر در ROUTES.

## نکات
- پوشه‌ها را با همین ساختار در GitHub بگذارید (کنار `app.py` و `requirements.txt`).
- کلیدهای Gemini را فقط در Streamlit ← Settings ← Secrets بگذارید: `GEMINI_API_KEYS = ["کلید-اول", "کلید-دوم"]`
- `data.json` را به GitHub نفرستید (در `.gitignore` هست). قبل از هر به‌روزرسانی، اسکریپت‌ها را با «Word» دانلود کنید.
