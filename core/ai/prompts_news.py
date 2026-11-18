"""پرامپت‌های «بررسی خبر»، «نظریه‌های توطئه» و «پرسش تکمیلی» (فارسی برای Gemini، انگلیسی برای Groq)."""


RESEARCH_RULES = (
    "تو دستیار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و پاسخ را به زبان فارسی، "
    "کامل، دقیق و با جزئیات بنویس (محدودیتی برای طول نیست). اعداد، تاریخ‌ها، نام افراد و شرکت‌ها را بیاور. "
    "هر ادعای مهم را با نام منبع همراه کن. هرگز خودت لینک نساز؛ لینک منابع واقعی بعد از متن "
    "به‌صورت خودکار اضافه می‌شود. اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)
NEWS_RULES = (
    "تو ویراستار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. با جست‌وجوی وب تحقیق کن و فقط مهم‌ترین و ضروری‌ترین "
    "اطلاعات را به فارسی روان و بدون غلط املایی بنویس. اعداد، تاریخ‌ها و نام‌ها را بیاور و هر ادعای مهم را با "
    "نام منبعش همراه کن. هرگز خودت لینک نساز؛ لینک منابع بعد از متن خودکار اضافه می‌شود. "
    "اگر دربارهٔ درستی چیزی مطمئن نیستی، صریحاً بگو.\n\n"
)
NEWS_STRUCTURE = (
    "قالب پاسخ (دقیقاً با همین عنوان‌ها و به‌صورت مارک‌داون؛ فقط مهم‌ترین و ضروری‌ترین اطلاعات؛ بدون مقدمه، "
    "بدون جملهٔ تکراری و بدون هیچ توضیحی دربارهٔ خودِ گزارش):\n"
    "## ۱) خلاصهٔ ساده\n"
    "۸ تا ۱۲ جمله برای مخاطب عمومی (سطح کلاس ششم)، در این ترتیب: اول ماجرا چیست و چه اتفاقی افتاد؛ بعد چرا مهم است "
    "و چه تأثیری روی زندگی آدم‌ها دارد؛ هر اصطلاح فنی را همان‌جا با یک جملهٔ ساده توضیح بده؛ و در پایان یک مثال "
    "ملموس از زندگی روزمره یا یک تشبیه ساده بیاور که مفهوم اصلی خبر را قابل‌فهم کند، با برچسب «**مثال:**» "
    "(مثال فقط برای فهم است و نباید ادعای واقعیِ تازه‌ای باشد).\n"
    "## ۲) حقایق و آمار کلیدی\nحداکثر ۶ نقطه (• ...)؛ هر کدام یک خط شامل عدد/تاریخ/نام و ارجاع به منبع.\n"
    "## ۳) پیشینه\nحداکثر ۳ نقطه.\n"
    "## ۴) محدودیت‌ها و میزان اطمینان\nحداکثر ۴ نقطه؛ آخرین نقطه: اطمینان کلی (زیاد/متوسط/کم) با یک دلیل.\n"
    "## ۵) زاویه‌های پیشنهادی برای ویدیو\n۳ زاویه، هر کدام یک خط.\n"
    "## ۶) نظریه‌ها و شایعات توطئه‌آمیز\n"
    "این بخش برای من مهم است و باید دقیق‌تر و مفصل‌تر از بقیه باشد. برای هر ادعا (حداکثر ۴ ادعا) دقیقاً این قالب:\n"
    "### ادعا: (یک جمله)\n"
    "- **چه کسی یا کدام منبع:** نام کامل، سمت یا رسانه، و بستر (توییتر/X، مصاحبه، مقاله، پادکست، انجمن…)\n"
    "- **دقیقاً چه گفته:** نقل‌قول کوتاه یا خلاصهٔ نزدیک به متن، همراه تاریخ اگر هست\n"
    "- **مستندات له و علیه:** چه چیزی آن را تقویت می‌کند و چه چیزی رد می‌کند\n"
    "- **نظر منابع معتبر یا راستی‌آزمایان:** (یا «موردی یافت نشد»)\n"
    "- **برچسب:** ادعای اثبات‌نشده\n"
    "اگر موردی در منابع نبود فقط بنویس «در منابع بررسی‌شده موردی یافت نشد»؛ هیچ ادعا، گوینده یا نقل‌قولی نساز.\n"
    "خبر: {title} — {desc}"
)
NEWS_PROMPT = NEWS_RULES + NEWS_STRUCTURE
FOLLOWUP_RULES = RESEARCH_RULES + (
    "این یک پرسش تکمیلی دربارهٔ تحقیقی است که قبلاً انجام شده. فقط به سؤال جدید پاسخ بده و اطلاعات تازه، "
    "دقیق و مستند بیاور؛ مطالب نسخه‌های قبلی را تکرار نکن، مگر برای تصحیح یک اشتباه.\n\n"
)


def build_followup_prompt(item, question, max_chars=14000):
    """پرسش جدید را همراه خلاصهٔ نسخه‌های قبلی (بدون بخش منابع) برای مدل آماده می‌کند."""
    parts, used = [], 0
    for v in reversed(item.get("research", [])):
        body = v["text"].split("\n\n---\n")[0]
        block = f"[نسخه {v['v']}" + (f" — سؤال: {v['q']}" if v.get("q") else "") + f"]\n{body}"
        if used + len(block) > max_chars:
            break
        parts.insert(0, block)
        used += len(block)
    return (FOLLOWUP_RULES + f"خبر: {item['title']} — {item['desc']}\n\n"
            "تحقیق‌ها و پرسش‌های قبلی:\n" + "\n\n".join(parts)
            + f"\n\nسؤال یا درخواست جدید: {question}")


GROQ_NEWS_PROMPT = (
    "Research this technology news item using web search (search in both English and Persian).\n"
    "News item: {title} - {desc}\n\n"
    "Write concise research notes in two parts.\n"
    "PART A - FACTS (about 350 words): key facts with numbers, dates and names; technical details; background; "
    "limitations and criticism. Name the source and the publication date of every claim.\n"
    "PART B - CONSPIRACY THEORIES AND RUMORS (about 450 words; this part is important): find the specific "
    "conspiracy theories, rumors and unverified speculation about this item. For EACH one (max 4) give: "
    "(1) the claim in one sentence; (2) WHO said it: full name, role or outlet, and where (X/Twitter, interview, "
    "article, podcast, forum); (3) WHAT exactly they said: a short direct quote or a close paraphrase, and the date; "
    "(4) the evidence offered for it and the evidence against it; (5) what credible outlets or fact-checkers say "
    "about it; (6) the URL of the page where you found it. If you find none, say exactly that. "
    "Never invent a speaker, a quote or a URL."
)
GROQ_CONSPIRACY_PROMPT = (
    "Use web search (English and Persian) to dig deeper into the conspiracy theories, rumors and unverified "
    "speculation around this technology news item.\nNews item: {title} - {desc}\n\n"
    "For EACH distinct claim (max 6) give: (1) the claim in one sentence; (2) WHO said it: full name, role or "
    "outlet, and where (X/Twitter, interview, article, podcast, forum); (3) WHAT exactly they said: a short direct "
    "quote or close paraphrase, and the date; (4) the evidence offered for it and the evidence against it; "
    "(5) what credible outlets or fact-checkers say; (6) the URL of the page where you found it. "
    "Be specific; no vague statements like 'some people say'. If you find none, say exactly that. "
    "Never invent a speaker, a quote or a URL."
)
CONSPIRACY_FORMAT = (
    "قالب پاسخ (مارک‌داون؛ بدون مقدمه و بدون توضیح دربارهٔ گزارش). عنوان: ## نظریه‌ها و شایعات توطئه‌آمیز\n"
    "برای هر ادعا (حداکثر ۶ ادعا) دقیقاً این قالب:\n"
    "### ادعا: (یک جمله)\n"
    "- **چه کسی یا کدام منبع:** نام کامل، سمت یا رسانه، و بستر (توییتر/X، مصاحبه، مقاله، پادکست، انجمن…)\n"
    "- **دقیقاً چه گفته:** نقل‌قول کوتاه یا خلاصهٔ نزدیک به متن، همراه تاریخ اگر هست\n"
    "- **مستندات له و علیه:** چه چیزی آن را تقویت می‌کند و چه چیزی رد می‌کند\n"
    "- **نظر منابع معتبر یا راستی‌آزمایان:** (یا «موردی یافت نشد»)\n"
    "- **برچسب:** ادعای اثبات‌نشده\n"
    "در پایان یک جمع‌بندی دو خطی. اگر موردی در منابع نبود فقط بنویس «در منابع بررسی‌شده موردی یافت نشد»؛ "
    "هیچ ادعا، گوینده یا نقل‌قولی نساز.\nخبر: {title} — {desc}"
)
FROM_SOURCES_RULES = (
    "تو ویراستار تحقیق یک کانال تکنولوژی فارسی‌زبان هستی. مواد زیر را یک موتور جست‌وجو از وب جمع کرده است "
    "(هر منبع یک شماره دارد). فقط بر اساس همین مواد بنویس. هر عدد، تاریخ، نقل‌قول و ادعا باید با ارجاع شماره‌ای "
    "مثل [3] یا [2][5] همراه باشد؛ چیزی که در مواد نیست نیاور، حتی اگر خودت می‌دانی. "
    "تاریخ امروز {today} است؛ تاریخی بعد از امروز را فقط اگر صریحاً در مواد آمده باشد بیاور و کنارش بنویس «طبق منبع». "
    "فقط «مثال:» در بخش خلاصهٔ ساده می‌تواند از خودت باشد (تشبیه ساده، بدون ادعای واقعی تازه). "
    "فارسی روان و بدون غلط املایی؛ هیچ عبارت داخل کروشه جز ارجاع‌های شماره‌ای ننویس؛ لینک نساز.\n\n"
)
