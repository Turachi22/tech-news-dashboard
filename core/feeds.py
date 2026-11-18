"""جمع‌آوری خودکار خبرهای تکنولوژی از منابع ساختاریافته (بدون هیچ سهمیهٔ جست‌وجو).

لایه‌ها:
  ۰) فیدهای RSS منابع منتخب هر حوزه (FEEDS) — مهم‌ترین منبع و بالاترین اولویت
  ۱) جست‌وجوی موضوعی Google News RSS برای هر حوزه (NEWS_QUERIES) — پوشش هزاران سایت دیگر
  ۲) Hacker News (API رایگان Algolia) — فقط برای «وایرال/بحث‌برانگیز بودن» (امتیاز و تعداد نظرها)
خروجی collect(): فهرست کاندیداهای رتبه‌بندی‌شده؛ Gemini از میان آن‌ها بهترین‌ها را انتخاب و فارسی می‌کند.

هر منبع جداگانه و با مهلت کوتاه گرفته می‌شود؛ اگر منبعی خراب یا مسدود بود، بی‌صدا کنار می‌رود.
برای دیدن وضعیت هر منبع: تنظیمات ← «تست منابع خبر». برای افزودن/حذف سایت، فقط فهرست FEEDS را ویرایش کنید.
"""
import datetime as dt
import html
import json
import math
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, wait
from email.utils import parsedate_to_datetime

import streamlit as st

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

_STOP = set("the a an of to in on for and is are with as at by from its it new after how why what this that be has have "
            "will says say over into more than about their his her you your can could may not but out up".split())


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
_KW = {d: re.compile(p, re.I) for d, p in KEYWORDS.items()}


def classify(text):
    """حوزهٔ محتمل یک خبر یا None (بیشترین تطابق کلیدواژه)."""
    best, n = None, 0
    for d, rx in _KW.items():
        k = len(rx.findall(text))
        if k > n:
            best, n = d, k
    return best


# ── دریافت و تجزیهٔ فید ─────────────────────────────────────────────────────────────────
def _fetch(url, timeout=TIMEOUT, max_bytes=3_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, "
                                                                          "application/xml, text/xml, application/json, */*"})
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310  (آدرس‌ها ثابت و معتبرند)
                return r.read(max_bytes)
        except urllib.error.HTTPError as exc:
            if attempt == 2 or exc.code not in (429, 500, 502, 503):
                raise
            time.sleep(1.5)


def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _text(el):
    return (el.text or "").strip() if el is not None else ""


def _clean(s, n=200):
    s = re.sub(r"<[^>]+>", " ", html.unescape(s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def _parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError, IndexError):
        try:
            d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d is None:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.astimezone(dt.timezone.utc)


def parse_feed(data, default_source=""):
    """RSS 2.0 و Atom را می‌خواند. خروجی: فهرست {title, url, published, source, desc}."""
    if b"<!ENTITY" in data[:5000]:
        raise ValueError("فید مشکوک (ENTITY)")
    root = ET.fromstring(data)
    items = []
    for el in root.iter():
        kind = _local(el.tag)
        if kind not in ("item", "entry"):
            continue
        f = {}
        for ch in el:
            name = _local(ch.tag)
            if name == "link" and kind == "entry":
                if ch.get("rel", "alternate") == "alternate" and ch.get("href"):
                    f.setdefault("link", ch.get("href"))
            elif name == "source":
                f["source"] = _text(ch)
            elif name in ("title", "link", "pubDate", "published", "updated", "date", "description", "summary", "encoded"):
                f.setdefault(name, _text(ch))
        title = _clean(f.get("title"), 300)
        pub = _parse_date(f.get("pubDate") or f.get("published") or f.get("date") or f.get("updated"))
        if not title or not pub or not f.get("link"):
            continue
        items.append({"title": title, "url": f["link"], "published": pub,
                      "source": f.get("source") or default_source,
                      "desc": _clean(f.get("description") or f.get("summary") or f.get("encoded"))})
    return items


def _gn_url(query, days):
    q = urllib.parse.quote_plus(f"{query} when:{days}d")
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def _job_feed(domain, name, url, tier, strip_source=False):
    items = parse_feed(_fetch(url), name)
    for it in items:
        it["domain"], it["tier"] = domain, tier
        if strip_source and " - " in it["title"]:     # عنوان‌های Google News: «تیتر - نام منبع»
            head, _, tail = it["title"].rpartition(" - ")
            it["title"] = head or it["title"]
            it["source"] = it["source"] or tail
    return items


def _fetch_hn(start_dt):
    ts = int(start_dt.timestamp())
    params = urllib.parse.urlencode({"tags": "story", "hitsPerPage": 100,
                                     "numericFilters": f"created_at_i>{ts},points>{HN_MIN_POINTS}"})
    data = json.loads(_fetch("https://hn.algolia.com/api/v1/search_by_date?" + params))
    out = []
    for h in data.get("hits", []):
        if not h.get("title") or not h.get("url") or h["title"].startswith(("Show HN", "Ask HN", "Tell HN", "Launch HN")):
            continue
        pub = dt.datetime.fromtimestamp(h.get("created_at_i", 0), dt.timezone.utc)
        out.append({"title": h["title"], "url": h["url"], "published": pub, "points": h.get("points") or 0,
                    "comments": h.get("num_comments") or 0, "hn_id": h.get("objectID")})
    return out


# ── خوشه‌بندی و امتیازدهی ───────────────────────────────────────────────────────────────
def _tokens(title):
    return {w for w in re.sub(r"[^a-z0-9\s]", " ", title.lower()).split()
            if (len(w) > 2 or any(ch.isdigit() for ch in w)) and w not in _STOP}


def _same(a, b):
    inter = len(a & b)
    if inter < 2:
        return False
    return inter / min(len(a), len(b)) >= 0.6 or (inter >= 3 and inter / len(a | b) >= 0.4)


def _norm_url(u):
    p = urllib.parse.urlparse(u)
    return p.netloc.lower().removeprefix("www.") + p.path.rstrip("/")


def _cluster(items):
    """مقاله‌های مربوط به یک رویداد را یکی می‌کند؛ تعداد منابع مستقل = معیار پوشش (وایرال‌بودن)."""
    items = sorted(items, key=lambda i: (-i["tier"], -i["published"].timestamp()))
    clusters = []
    for it in items:
        toks = it.setdefault("_t", _tokens(it["title"]))
        for c in clusters:
            if _same(toks, c["_t"]):
                c["members"].append(it)
                c["_t"] |= toks
                break
        else:
            clusters.append({"_t": set(toks), "members": [it]})
    return clusters


def _fa_ok(domain):
    return DOMAIN_FA.get(domain, "")


def _build(items, hn, start_dt, end_dt):
    window = max((end_dt - start_dt).total_seconds(), 1)
    cands = []
    used_hn = set()
    for c in _cluster(items):
        m = c["members"]
        lead = m[0]
        sources = []
        for x in m:
            if x["source"] and x["source"] not in sources:
                sources.append(x["source"])
        domains = [x["domain"] for x in m if x["domain"] != "general"]
        domain = max(set(domains), key=domains.count) if domains else (
            classify(lead["title"] + " " + lead["desc"]) or "general")
        pts = com = 0
        urls = {_norm_url(x["url"]) for x in m}
        for h in hn:
            if h["hn_id"] in used_hn:
                continue
            if _norm_url(h["url"]) in urls or _same(_tokens(h["title"]), c["_t"]):
                pts, com = max(pts, h["points"]), max(com, h["comments"])
                used_hn.add(h["hn_id"])
        newest = max(x["published"] for x in m)
        cands.append({"title": lead["title"], "url": lead["url"], "date": newest.date().isoformat(),
                      "sources": sources[:4], "n_sources": len(sources), "domain": domain,
                      "points": pts, "comments": com, "desc": next((x["desc"] for x in m if x["desc"]), ""),
                      "tier": max(x["tier"] for x in m), "fresh": 1 - (end_dt - newest).total_seconds() / window})
    for h in hn:   # خبرهای داغ HN که هیچ‌کدام از فیدها نداشتند
        if h["hn_id"] in used_hn or h["points"] < HN_MIN_POINTS * 2:
            continue
        hn_domain = classify(h["title"])
        if not hn_domain:      # خارج از ۸ حوزه (بانک، سیاست، مسائل اجتماعی...)
            continue
        host = urllib.parse.urlparse(h["url"]).netloc.removeprefix("www.")
        cands.append({"title": h["title"], "url": h["url"], "date": h["published"].date().isoformat(),
                      "sources": [host], "n_sources": 1, "domain": hn_domain, "points": h["points"],
                      "comments": h["comments"], "desc": "", "tier": 0.4,
                      "fresh": 1 - (end_dt - h["published"]).total_seconds() / window})
    for c in cands:
        c["fresh"] = min(1, max(0, c["fresh"]))
        controversy = 0.5 if (c["comments"] >= 150 and c["points"] and c["comments"] / c["points"] >= 0.6) else 0
        c["score"] = round(3 * min(1, (c["n_sources"] - 1) / 4) + 3 * min(1, math.log10(1 + c["points"]) / 3)
                           + 1.5 * min(1, c["comments"] / 400) + controversy + 1.5 * c["fresh"] + 0.5 * c["tier"], 3)
    return cands


def _select(cands):
    """بهترین‌های هر حوزه (متعادل)، سپس شماره‌گذاری."""
    by = {}
    for c in sorted(cands, key=lambda x: -x["score"]):
        by.setdefault(c["domain"], []).append(c)
    chosen = []
    for d, lst in by.items():
        chosen += lst[: GENERAL_TOP if d == "general" else PER_DOMAIN]
    chosen = sorted(chosen, key=lambda x: -x["score"])[:MAX_CANDIDATES]
    for i, c in enumerate(chosen, 1):
        c["id"] = i
    return chosen


# ── نقطهٔ ورود ─────────────────────────────────────────────────────────────────────────────
def collect(start, end, refresh=False):
    """خبرهای منتشرشده بین دو تاریخ (شامل هر دو) را از همهٔ لایه‌ها می‌گیرد.
    خروجی: (کاندیداهای رتبه‌بندی‌شده، گزارش سلامت منابع {نام: (ok, تعداد, خطا)})؛ نتیجه ۲۰ دقیقه کش می‌شود."""
    ss = st.session_state
    key = (start.isoformat(), end.isoformat())
    cached = ss.get("_feeds_cache")
    if cached and not refresh and cached[0] == key and time.time() - cached[1] < CACHE_SECONDS:
        return cached[2], cached[3]

    start_dt = dt.datetime.combine(start, dt.time.min, dt.timezone.utc)
    end_dt = dt.datetime.combine(end, dt.time.max, dt.timezone.utc)
    days = max((end - start).days, 1)
    jobs = []   # (برچسب، تابع)
    for domain, lst in FEEDS.items():
        for name, url in lst:
            jobs.append((f"{name}", lambda d=domain, n=name, u=url: _job_feed(d, n, u, 1.0)))
    for domain, queries in NEWS_QUERIES.items():
        for i, q in enumerate(queries, 1):
            jobs.append((f"Google News · {domain} #{i}",
                         lambda d=domain, q=q: _job_feed(d, "Google News", _gn_url(q, days), 0.6, strip_source=True)))
    jobs.append(("Hacker News", lambda: _fetch_hn(start_dt)))

    health, items, hn = {}, [], []
    pool = ThreadPoolExecutor(max_workers=WORKERS)
    futures = {pool.submit(fn): label for label, fn in jobs}
    done, pending = wait(futures, timeout=BUDGET)
    for f in done:
        label = futures[f]
        try:
            res = f.result()
        except Exception as exc:  # noqa: BLE001
            health[label] = (False, 0, f"{type(exc).__name__}: {str(exc)[:80]}")
            continue
        if label == "Hacker News":
            hn = res
            health[label] = (True, len(res), "")
            continue
        inside = [i for i in res if start_dt <= i["published"] <= end_dt + dt.timedelta(days=1)]
        items += inside
        health[label] = (True, len(inside), "")
    for f in pending:
        health[futures[f]] = (False, 0, "مهلت تمام شد")
        f.cancel()
    pool.shutdown(wait=False, cancel_futures=True)

    seen, uniq = set(), []
    for it in items:   # حذف تکراری‌های هم‌آدرس
        k = _norm_url(it["url"])
        if k not in seen:
            seen.add(k)
            uniq.append(it)
    cands = _select(_build(uniq, hn, start_dt, end_dt))
    ss["_feeds_cache"] = (key, time.time(), cands, health)
    return cands, health


def shortlist(cands, per_domain=4, general=6):
    """نسخهٔ کوچک‌تر فهرست برای Groq (سقف توکن در دقیقهٔ پلن رایگان کم است)؛ شماره‌ها (id) همان می‌مانند."""
    count, out = {}, []
    for c in cands:           # cands از قبل بر اساس امتیاز مرتب است
        d = c["domain"]
        if count.get(d, 0) < (general if d == "general" else per_domain):
            count[d] = count.get(d, 0) + 1
            out.append(c)
    return out


def format_candidates(cands, snippet=200):
    lines = []
    for c in cands:
        hn = f" | HN: {c['points']} pts, {c['comments']} comments" if c["points"] else ""
        cov = f" | {c['n_sources']} independent sources" if c["n_sources"] > 1 else ""
        snip = f" | {c['desc'][:snippet]}" if c["desc"] else ""
        lines.append(f"[{c['id']}] ({c['domain']}) {c['title']} — {', '.join(c['sources'])} | {c['date']}{hn}{cov}{snip}")
    return "\n".join(lines)


def health_report():
    """برای دکمهٔ «تست منابع خبر» در تنظیمات."""
    today = dt.date.today()
    start = today - dt.timedelta(days=3)
    cands, health = collect(start, today, refresh=True)
    ok = [k for k, v in health.items() if v[0]]
    bad = [(k, v[2]) for k, v in health.items() if not v[0]]
    empty = [k for k, v in health.items() if v[0] and v[1] == 0]
    st.markdown(f"**{len(ok)} منبع از {len(health)} پاسخ داد** · {len(cands)} کاندیدای رتبه‌بندی‌شده")
    if bad:
        st.warning("منابع ناموفق (اشکالی ندارد؛ خودکار کنار گذاشته می‌شوند):\n\n" +
                   "\n".join(f"- {k} — {e}" for k, e in bad))
    if empty:
        st.caption("بدون خبر در ۳ روز اخیر: " + "، ".join(empty))
    by = {}
    for c in cands:
        by[c["domain"]] = by.get(c["domain"], 0) + 1
    st.caption("کاندیداها به تفکیک حوزه: " + "، ".join(f"{d}: {n}" for d, n in by.items()))
    for c in cands[:8]:
        st.markdown(f"- **{c['score']}** · [{c['domain']}] {c['title']} _({', '.join(c['sources'][:2])}، {c['date']}"
                    + (f"، HN {c['points']}" if c["points"] else "") + ")_")
