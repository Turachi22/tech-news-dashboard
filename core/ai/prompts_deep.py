"""پرامپت‌های سناریوی دیپ‌دایو (۸ بخش + متن کامل نریشن)."""


GROQ_DEEP_PROMPT = (
    "Use web search to research this topic for a documentary-style video. Prefer primary and reputable sources "
    "(official sites, papers, major outlets, interviews, archives).\nTopic: {title}\n\n"
    "Collect, with the exact URL of the page for EVERY item: (1) a timeline of key events with verified dates; "
    "(2) the core facts and numbers; (3) surprising, little-known but verified details and anecdotes; "
    "(4) common myths or exaggerated claims about the topic, and for each the evidence for and against and what "
    "credible sources say; (5) short direct quotes with speaker, date and source; (6) weakly sourced claims, "
    "clearly marked as unverified. Be specific. Never invent a fact, date, quote or URL; if something cannot be "
    "verified, say so."
)
DEEP_FORMAT = (
    "یک سناریوی کامل ویدیوی یوتیوب (مینی‌مستند) دربارهٔ موضوع زیر بنویس. قالب (مارک‌داون، دقیقاً با همین عنوان‌ها، "
    "بدون مقدمه و بدون توضیح دربارهٔ خودِ گزارش):\n"
    "## ۱) قلاب ۳۰ ثانیه‌ای\nافتتاحیه‌ای کوتاه و میخکوب‌کننده (سؤال یا تصویر عجیب)، حداکثر حدود ۷۰ کلمه.\n"
    "## ۲) تز اصلی\nیک یا دو جمله: ادعای اصلی ویدیو.\n"
    "## ۳) خط زمان با تاریخ‌های راستی‌آزمایی‌شده\nنقطه‌ها (• تاریخ — رویداد [n]).\n"
    "## ۴) سه زاویهٔ روایی\nسه زاویه، هر کدام یک خط، و یکی را به‌عنوان زاویهٔ پیشنهادی علامت بزن.\n"
    "## ۵) صحنه‌به‌صحنه با پیشنهاد تصویر\nهر صحنه: عنوان، زمان تقریبی، یک خط محتوا و «تصویر:» پیشنهادی.\n"
    "## ۶) افسانه یا واقعیت؟\nهر مورد: ادعا، سپس مدرک له و علیه با ارجاع [n]، و حکم.\n"
    "## ۷) نقل‌قول‌ها و منابع\nفقط نقل‌قول‌های موجود در مواد، با گوینده و تاریخ [n].\n"
    "## ۸) ادعاهای تأییدنشده\nهر ادعای ضعیف را با برچسب «تأییدنشده» بیاور؛ اگر نبود بنویس «موردی یافت نشد».\n"
    "## ۹) متن کامل نریشن\n"
    "متن آمادهٔ خواندن برای گوینده، حدود ۱۲۰۰ تا ۱۵۰۰ کلمه (۸ تا ۱۰ دقیقه)، برای مخاطب کم‌سواد: فارسی ساده و "
    "محاوره‌ای، جمله‌های کوتاه، بدون اصطلاح پیچیده (هر اصطلاح فنی را همان‌جا با مثال روزمره باز کن)، با زاویه‌ای "
    "کنجکاوی‌برانگیز و تفکربرانگیز که بیننده را میخکوب کند، لحن شوخ‌طبع و صمیمی مثل تعریف‌کردن برای دوست. "
    "فقط حقایق همین مواد را روایت کن؛ شوخی و تشبیه فقط برای فهم است و نباید ادعای واقعی تازه باشد. "
    "ادعای ضعیف را در نریشن با «می‌گن»/«ظاهراً» و بدون قطعیت بگو. "
    "در ابتدای هر صحنه یک خط «[تصویر: ...]» بگذار. ارجاع [n] را در نریشن نیاور؛ ارجاع‌ها فقط در بخش‌های ۱ تا ۸ باشد.\n"
    "موضوع: {title}"
)
DEEP_STYLE_OVERRIDE = (
    "استثنا برای بخش «متن کامل نریشن»: تشبیه، مثال روزمره و شوخی از خودت مجاز است، به شرطی که ادعای واقعیِ "
    "تازه نباشد.\n\n"
)
