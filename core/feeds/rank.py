"""خوشه‌بندی خبرهای تکراری، تشخیص حوزه و امتیازدهی کاندیدها."""
import math
import re
import urllib.parse

from core.feeds.config import GENERAL_TOP, HN_MIN_POINTS, MAX_CANDIDATES, PER_DOMAIN
from core.feeds.sources import DOMAIN_FA, KEYWORDS


_STOP = set("the a an of to in on for and is are with as at by from its it new after how why what this that be has have "
            "will says say over into more than about their his her you your can could may not but out up".split())

_KW = {d: re.compile(p, re.I) for d, p in KEYWORDS.items()}


def classify(text):
    """حوزهٔ محتمل یک خبر یا None (بیشترین تطابق کلیدواژه)."""
    best, n = None, 0
    for d, rx in _KW.items():
        k = len(rx.findall(text))
        if k > n:
            best, n = d, k
    return best


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
