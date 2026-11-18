"""فهرست منابع خبر (فقط داده). برای افزودن یا حذف سایت، همین فایل را ویرایش کنید: FEEDS = فیدهای RSS هر حوزه، NEWS_QUERIES = جست‌وجوهای Google News، KEYWORDS = تشخیص حوزه."""

# ── حوزه‌ها ──────────────────────────────────────────────────────────────────────────────
DOMAIN_FA = {
    "biology": "زیست‌شناسی و پزشکی", "machines": "ماشین‌آلات و روبات", "ai": "هوش مصنوعی",
    "space": "فضا", "defense": "تسلیحات و دفاع", "software": "نرم‌افزار و امنیت",
    "energy": "انرژی و مواد", "chips": "تراشه و محاسبات", "general": "",
}

# ── لایهٔ ۰: منابع منتخب (نام، آدرس فید). «general» = منبع عمومی؛ حوزه را Gemini تشخیص می‌دهد ──
FEEDS = {
    "biology": [
        ("STAT (زیست‌فناوری)", "https://www.statnews.com/category/biotech/feed/"),
        ("Fierce Biotech", "https://www.fiercebiotech.com/rss/xml"),
        ("Science News", "https://www.sciencenews.org/feed"),
        ("New Scientist", "https://www.newscientist.com/feed/home/"),
        ("Labiotech", "https://www.labiotech.eu/feed/"),
        ("Phys.org Biology", "https://phys.org/rss-feed/biology-news/"),
        ("Medical Xpress", "https://medicalxpress.com/rss-feed/"),
    ],
    "machines": [
        ("IEEE Spectrum", "https://spectrum.ieee.org/feeds/feed.rss"),
        ("The Robot Report", "https://www.therobotreport.com/feed/"),
        ("New Atlas Robotics", "https://newatlas.com/robotics/index.rss"),
        ("Electrek", "https://electrek.co/feed/"),
        ("Interesting Engineering", "https://interestingengineering.com/feed"),
        ("Tech Xplore Robotics", "https://techxplore.com/rss-feed/robotics-news/"),
        ("TechCrunch Robotics", "https://techcrunch.com/category/robotics/feed/"),
    ],
    "ai": [
        ("MIT Technology Review", "https://www.technologyreview.com/feed/"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("Ars Technica AI", "https://arstechnica.com/ai/feed/"),
        ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
        ("OpenAI News", "https://openai.com/news/rss.xml"),
        ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ],
    "space": [
        ("Space.com", "https://www.space.com/feeds.xml"),
        ("SpaceNews", "https://spacenews.com/feed/"),
        ("NASA", "https://www.nasa.gov/feed/"),
        ("Universe Today", "https://www.universetoday.com/feed"),
        ("Payload", "https://payloadspace.com/feed"),
        ("Ars Technica Space", "https://arstechnica.com/space/feed/"),
        ("TechCrunch Space", "https://techcrunch.com/category/space/feed/"),
    ],
    "defense": [
        ("Breaking Defense", "https://breakingdefense.com/full-rss-feed/"),
        ("The War Zone", "https://www.twz.com/feed"),
        ("Defense One (فناوری)", "https://www.defenseone.com/rss/technology/"),
        ("DefenseScoop", "https://defensescoop.com/feed/"),
        ("Naval News", "https://www.navalnews.com/feed/"),
        ("Defence Blog", "https://defence-blog.com/feed"),
        ("Army Technology", "https://www.army-technology.com/feed/"),
        ("Airforce Technology", "https://www.airforce-technology.com/feed/"),
    ],
    "software": [
        ("BleepingComputer", "https://www.bleepingcomputer.com/feed/"),
        ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews"),
        ("Krebs on Security", "https://krebsonsecurity.com/feed/"),
        ("CyberScoop", "https://cyberscoop.com/feed/"),
        ("The Register", "https://www.theregister.com/headlines.atom"),
        ("TechCrunch Security", "https://techcrunch.com/category/security/feed/"),
        ("Ars Technica Security", "https://arstechnica.com/security/feed/"),
        ("Wired Security", "https://www.wired.com/feed/category/security/latest/rss"),
    ],
    "energy": [
        ("CleanTechnica", "https://cleantechnica.com/feed/"),
        ("Canary Media", "https://www.canarymedia.com/rss.rss"),
        ("New Atlas Energy", "https://newatlas.com/energy/index.rss"),
        ("Phys.org Nanotech", "https://phys.org/rss-feed/nanotech-news/"),
    ],
    "chips": [
        ("Tom's Hardware", "https://www.tomshardware.com/feeds/all"),
        ("IEEE Spectrum Semiconductors", "https://spectrum.ieee.org/feeds/topic/semiconductors.rss"),
        ("EE Times", "https://www.eetimes.com/feed/"),
        ("The Quantum Insider", "https://thequantuminsider.com/feed/"),
        ("ServeTheHome", "https://www.servethehome.com/feed/"),
        ("Phys.org Quantum", "https://phys.org/rss-feed/physics-news/quantum-physics/"),
    ],
    "general": [
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("Wired", "https://www.wired.com/feed/rss"),
        ("Phys.org", "https://phys.org/rss-feed/"),
    ],
}

# ── لایهٔ ۱: جست‌وجوهای Google News (انگلیسی؛ بازهٔ زمانی خودکار اضافه می‌شود) ──────────────────
NEWS_QUERIES = {
    "biology": ["gene editing OR CRISPR OR gene therapy breakthrough",
                "brain-computer interface OR longevity OR lab-grown OR new drug breakthrough"],
    "machines": ["humanoid robot OR robotics breakthrough", "autonomous vehicle OR eVTOL OR drone new technology"],
    "ai": ["new AI model release OR AI breakthrough", "artificial intelligence safety OR regulation OR controversy"],
    "space": ["NASA OR ESA OR telescope discovery", "rocket launch OR satellite OR Moon OR Mars mission"],
    "defense": ["hypersonic OR new weapon OR military drone technology", "AI warfare OR autonomous weapons"],
    "software": ["cyberattack OR data breach OR zero-day vulnerability", "open source OR operating system OR privacy controversy"],
    "energy": ["fusion OR nuclear reactor OR solid-state battery breakthrough",
               "solar OR superconductor OR energy storage breakthrough"],
    "chips": ["semiconductor OR chip OR quantum computer breakthrough"],
}


# ── تشخیص حوزه با کلیدواژه (برای خبرهای فقط‌HN: خبر خارج از ۸ حوزه حذف می‌شود) ──
KEYWORDS = {
    "biology": r"gene|crispr|genom|\bdna\b|\brna\b|vaccine|drug|therap|cancer|clinical|\bfda\b|biotech|protein|"
               r"neuro|longevity|aging|medical|disease|virus|antibiotic|stem cell|organoid|lab-grown|surgery",
    "machines": r"robot|humanoid|drone|autonomous|self-driving|robotaxi|evtol|aircraft|airplane|\bjet\b|vehicle|"
                r"\bev\b|electric car|truck|exoskeleton|waymo|boston dynamics|optimus",
    "ai": r"\bai\b|artificial intelligence|\bllm|\bgpt|gemini|claude|openai|anthropic|deepmind|machine learning|"
          r"chatbot|neural|copilot|\bagents?\b",
    "space": r"\bspace|nasa|\besa\b|rocket|satellite|\bmoon\b|lunar|\bmars\b|orbit|telescope|asteroid|astronaut|"
             r"comet|galax|starship|spacex",
    "defense": r"military|missile|hypersonic|weapon|pentagon|\barmy\b|\bnavy\b|air force|fighter|f-35|warfare|nato|"
               r"stealth|bomber|submarine|radar|defense",
    "software": r"software|windows|linux|macos|\bios\b|android|browser|open source|open-source|cyber|hack|breach|"
                r"vulnerab|zero-day|ransomware|malware|encrypt|privacy|exploit|\bcve|security",
    "energy": r"battery|batteries|solar|nuclear|fusion|reactor|power grid|hydrogen|superconduct|lithium|wind turbine|"
              r"geothermal|graphene|perovskite|energy storage",
    "chips": r"\bchips?\b|semiconductor|\bgpu|\bcpu|tsmc|nvidia|\bintel\b|\bamd\b|quantum|qubit|processor|"
             r"transistor|lithograph|\bhbm|silicon",
}
