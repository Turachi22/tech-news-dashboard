# داشبورد کانال ساده

هر بخش برنامه یک فایل کوچک و جدا دارد. موقع اصلاح، فقط همان فایل را عوض کنید؛ بقیه دست‌نخورده می‌مانند.

```
app.py                         ← منو (ROUTES) و مسیریابی صفحه‌ها
views/                         ← صفحه‌ها (فقط چیدمان کارت‌ها)
  home.py  news.py  deep.py  stats.py  settings.py

components/                    ← کارت‌های قابل‌استفادهٔ مجدد
  workflow.py                  ← کارت هر خبر، دسته‌بندی تأیید/رد/انتظار
  research_box.py              ← نسخه‌های تحقیق، پرسش تکمیلی، حالت دستی
  script_box.py                ← کادر اسکریپت (ویرایشگر رنگ/اندازه) + دادهٔ Word
  week_nav.py                  ← کلید هفتهٔ قبل/بعد
  ideas.py                     ← کارت دیپ‌دایو (سناریو، ویرایش نریشن، رد)
  rich_editor/index.html       ← خود ویرایشگر رنگ و اندازه (HTML/JS)
  sidebar.py  stats_card.py  calendar_card.py

core/
  ai/                          ← Gemini + Groq (نقشهٔ کامل در core/ai/__init__.py)
    config.py                  ← مدل‌ها و سقف مصرف (برای عوض‌کردن مدل)
    prompts_news.py            ← پرامپت بررسی خبر و نظریه‌های توطئه
    prompts_deep.py            ← پرامپت سناریوی دیپ‌دایو (۸ بخش + نریشن)
    prompts_suggest.py         ← معیارهای پیشنهاد خبر روزانه
    deep_ideas.py              ← معیار نمره‌دار پیشنهاد هفتگی دیپ‌دایو
    research.py  suggest_news.py  gemini.py  gemini_models.py  diagnostics.py  text_utils.py
  feeds/                       ← جمع‌آوری خبر از فیدها
    sources.py                 ← فهرست سایت‌ها (برای افزودن/حذف منبع)
    config.py  fetch.py  rank.py  collect.py
  style/                       ← ظاهر (CSS)
    base.py  cards.py  news.py  dashboard.py
  state.py  daily.py  deep_suggest.py  richtext.py  export.py
  helpers.py  auth.py  backup.py  storage.py  groq_client.py  pwa.py
```

## کدام بخش را کجا عوض کنم؟
| می‌خواهم... | فایل |
|---|---|
| منو یا صفحه اضافه/حذف کنم | `app.py` (ROUTES) |
| مدل‌های Gemini یا سقف مصرف | `core/ai/config.py` |
| معیارهای پیشنهاد خبر روزانه | `core/ai/prompts_suggest.py` |
| معیار/وزن نمره‌دهی موضوع‌های دیپ‌دایو | `core/ai/deep_ideas.py` (بالای فایل) |
| قالب سناریوی دیپ‌دایو یا نریشن | `core/ai/prompts_deep.py` |
| قالب بررسی خبر | `core/ai/prompts_news.py` |
| سایت‌های خبری (افزودن/حذف) | `core/feeds/sources.py` |
| رنگ‌ها و فونت | `core/style/base.py` (متغیرهای `:root`) |
| ظاهر کارت‌ها / دکمه‌ها / موبایل | `core/style/cards.py` · `news.py` · `dashboard.py` |
| رنگ و اندازهٔ ویرایشگر متن | `components/rich_editor/index.html` |
| زمان پیشنهاد هفتگی دیپ‌دایو (جمعه) | `core/deep_suggest.py` |
| قالب فایل Word | `core/export.py` |

## افزودن صفحهٔ جدید
1. فایل `views/report.py` با تابع `render()` بسازید.
2. در `app.py` دو خط اضافه کنید: `import report` در فهرست `from views import ...` و یک سطر در ROUTES.

## نکات
- پوشه‌ها را با همین ساختار در GitHub بگذارید (کنار `app.py` و `requirements.txt`).
- کلیدهای Gemini را فقط در Streamlit ← Settings ← Secrets بگذارید: `GEMINI_API_KEYS = ["کلید-اول", "کلید-دوم"]`
- `data.json` را به GitHub نفرستید. قبل از هر به‌روزرسانی، اسکریپت‌ها را با «Word» دانلود کنید.
