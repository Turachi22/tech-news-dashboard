"""دریافت و تجزیهٔ فیدهای RSS/Atom، Google News و Hacker News."""
import datetime as dt
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from core.feeds.config import HN_MIN_POINTS, TIMEOUT, UA


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
