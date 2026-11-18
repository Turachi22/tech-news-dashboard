"""پیشنهاد خبر روزانه: جمع‌آوری از فیدها، انتخاب با Gemini/Groq، حذف تکراری و محدودیت حوزه."""
import datetime as dt
import re

import streamlit as st

from core import feeds, groq_client
from core.ai.config import SEARCH_PRIORITY
from core.ai.gemini import ask_ai
from core.ai.prompts_suggest import (GROQ_SUGGEST_PROMPT, MUSK_RE, SUGGEST_FROM_CANDIDATES, SUGGEST_FROM_SOURCES,
                                     SUGGEST_PICK_EN, SUGGEST_PROMPT)
from core.ai.research import _groq_cached, _groq_note, _materials
from core.ai.text_utils import _similar
from core.groq_client import GroqError


def _parse_picks(text, cands, existing=(), english=False):
    """خروجی Gemini در حالت «انتخاب از فهرست»: شمارهٔ کاندید ← لینک، منبع و تاریخ واقعی از خود کاندید گرفته می‌شود
    (نه از مدل). تکراری‌ها، خبر قبلی، بیش از ۲ خبر در یک حوزه و بیش از یک خبر مرتبط با ماسک حذف می‌شود."""
    by_id = {c["id"]: c for c in cands}
    items, per_domain, musk = [], {}, 0
    body = text.partition("\n\n---\n")[0]
    for line in body.splitlines():
        parts = [x.strip(" *-•\t") for x in line.split("|")]
        if len(parts) < 3:
            continue
        m = re.search(r"\d+", parts[0])
        c = by_id.get(int(m.group(0))) if m else None
        if not c:
            continue
        title, summary = parts[1], parts[2]
        off = 0 if english else 1          # حالت انگلیسی (Groq): فیلد «حوزه» وجود ندارد
        domain = DOMAIN_FA_BY_KEY.get(c["domain"]) or (parts[3] if (not english and len(parts) > 3) else "")
        key = parts[3 + off] if len(parts) > 3 + off else ""
        debate = parts[4 + off] if len(parts) > 4 + off else ""
        if any(_similar(title, e) for e in existing):
            continue
        if any(_similar(title, i["title"]) or (key and i["key"] and _similar(key, i["key"], 0.6)) for i in items):
            continue
        if domain and per_domain.get(domain, 0) >= MAX_PER_DOMAIN:
            continue
        if MUSK_RE.search(c["title"] + " " + c["desc"]):
            if musk >= 1:
                continue
            musk += 1
        per_domain[domain] = per_domain.get(domain, 0) + 1
        if debate and debate not in ("-", "—", "–"):
            summary += f" · محل بحث: {debate}"
        signals = []
        if c["n_sources"] >= 3:
            signals.append(f"{c['n_sources']} منبع مستقل")
        if c["points"] >= 100:
            signals.append(f"{c['points']} امتیاز در Hacker News")
        if signals:
            summary += " · سیگنال: " + "، ".join(signals)
        items.append({"title": title, "desc": summary, "date": c["date"], "source": "، ".join(c["sources"][:2]),
                      "domain": domain, "key": key, "url": c["url"]})
    sources = ("**منابع (لینک مستقیم هر خبر):**\n" +
               "\n".join(f"{i}. [{it['source']}]({it['url']})" for i, it in enumerate(items, 1))) if items else ""
    return items, sources


def _from_feeds(start, end_date, n, avoid, existing, box):
    """لایهٔ ۰–۲: خبرها را از فیدها/Google News/HN می‌گیرد و Gemini (بدون جست‌وجو و بدون مصرف سهمیهٔ جست‌وجو) انتخاب می‌کند.
    اگر منبعی کم بود یا Gemini جواب نداد، None برمی‌گرداند تا جست‌وجوی قدیمی ادامه یابد."""
    try:
        cands, _health = feeds.collect(start, end_date)
    except Exception as exc:  # noqa: BLE001
        st.caption(f"جمع‌آوری از فیدها انجام نشد ({type(exc).__name__}) — جست‌وجوی هوشمند استفاده می‌شود.")
        return None
    if len(cands) < 8:
        st.caption("فیدها خبر کافی نداشتند — جست‌وجوی هوشمند استفاده می‌شود.")
        return None
    prompt = SUGGEST_FROM_CANDIDATES.format(n=n, start=start.isoformat(), end=end_date.isoformat(),
                                            avoid=avoid) + feeds.format_candidates(cands)
    text = ask_ai(prompt, box, ext_sources=[])   # ext_sources=[] ⇒ بدون جست‌وجوی گوگل
    if text:
        items, sources = _parse_picks(text, cands, existing)
        if items:
            return items, sources
    # Gemini جواب نداد (مثلاً سهمیه): Groq به انگلیسی و بدون جست‌وجو از همین فهرست انتخاب می‌کند
    if groq_client.available():
        try:
            short = feeds.shortlist(cands)
            gprompt = SUGGEST_PICK_EN.format(n=n, start=start.isoformat(), end=end_date.isoformat(),
                                             avoid=avoid) + feeds.format_candidates(short, snippet=110)
            gtext = groq_client.chat(gprompt)
        except GroqError as exc:
            _groq_note(exc)
            return None
        items, sources = _parse_picks(gtext, short, existing, english=True)
        if items:
            st.caption("Gemini در دسترس نبود؛ انتخاب با Groq (به انگلیسی) انجام شد. عنوان‌ها انگلیسی‌اند.")
            return items, sources
    return None


def suggest_news(end_date, days=3, n=5, existing=()):
    """خبرهای منتشرشده در بازهٔ [end_date - days, end_date] را پیشنهاد می‌دهد.
    اول Groq جست‌وجو می‌کند و Gemini خلاصه را به فارسی درمی‌آورد؛ اگر Groq نبود، Gemini با جست‌وجوی خودش.
    خروجی: (فهرست خبرها، متن بخش منابع). خبرِ بدون تاریخ معتبر یا خارج از بازه حذف می‌شود."""
    start = end_date - dt.timedelta(days=days)
    avoid = ("ALREADY USED headlines (do not repeat these or the same events): " + "; ".join(list(existing)[:15]) + "\n"
             if existing else "")
    box = st.empty()
    got = _from_feeds(start, end_date, n, avoid, existing, box)
    if got:
        box.empty()
        return got
    st.session_state["_last_ai_call"] = 0
    gem_prompt = SUGGEST_PROMPT.format(start=start.isoformat(), end=end_date.isoformat(), n=n, avoid=avoid)
    text, groq_done = None, False
    groq_ok = groq_client.available()
    if SEARCH_PRIORITY == "gemini":
        # اول جست‌وجوی خود Gemini (بی‌صدا اگر Groq هم هست)؛ فقط با جست‌وجوی واقعی، نه از حافظهٔ مدل
        text = ask_ai(gem_prompt, box, need_search=True, quiet=groq_ok)
        if text:
            box.empty()
            return _parse_suggestions(text, start, end_date, existing)
        st.session_state["_last_ai_call"] = 0
    if groq_ok:
        try:
            gtext, srcs = _groq_cached(GROQ_SUGGEST_PROMPT.format(
                n=n, start=start.isoformat(), end=end_date.isoformat(), avoid=avoid))
            if not srcs:
                raise GroqError("Groq لینک منبعی برنگرداند")
            groq_done = True
            prompt = SUGGEST_FROM_SOURCES.format(n=n, start=start.isoformat(), end=end_date.isoformat(),
                                                 avoid=avoid) + _materials(gtext, srcs)
            text = ask_ai(prompt, box, ext_sources=[(u, m["title"]) for u, m in srcs.items()])
            if not text:   # Gemini نتوانست بنویسد: خروجی انگلیسی خود Groq (همان قالب خطی) استفاده می‌شود
                text = gtext
                st.caption("Gemini در دسترس نبود؛ نتیجهٔ جست‌وجوی Groq (به انگلیسی) استفاده شد.")
        except GroqError as exc:
            _groq_note(exc)
    if not groq_done and not text and SEARCH_PRIORITY != "gemini":
        text = ask_ai(gem_prompt, box, need_search=True)
    box.empty()
    return _parse_suggestions(text, start, end_date, existing) if text else (None, "")


MAX_PER_DOMAIN = 2
DOMAIN_FA_BY_KEY = feeds.DOMAIN_FA


def _parse_suggestions(text, start, end_date, existing=()):
    """خطوط «عنوان | توضیح | تاریخ | منبع | حوزه | کلید خبر | محل بحث» را می‌خواند (سه فیلد آخر اختیاری).
    فقط خبرهای داخل بازهٔ تاریخ می‌ماند؛ خبر تکراری (کلید یا عنوان مشابه، یا مشابه خبرهای قبلی) حذف می‌شود
    و از هر حوزه حداکثر ۲ خبر می‌آید."""
    if not text:
        return None, ""
    body, _, sources = text.partition("\n\n---\n")
    items, per_domain = [], {}
    for line in body.splitlines():
        parts = [x.strip(" *-•\t") for x in line.split("|")]
        if len(parts) < 4:
            continue
        m = re.search(r"\d{4}-\d{2}-\d{2}", parts[2])
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(0))
        except ValueError:
            continue
        if not (start <= d <= end_date):
            continue
        title, summary, source = parts[0], parts[1], parts[3]
        domain = parts[4] if len(parts) > 4 else ""
        key = parts[5] if len(parts) > 5 else ""
        debate = parts[6] if len(parts) > 6 else ""
        if any(_similar(title, e) for e in existing):
            continue
        if any(_similar(title, i["title"]) or (key and i["key"] and _similar(key, i["key"], 0.6)) for i in items):
            continue
        if domain and per_domain.get(domain, 0) >= MAX_PER_DOMAIN:
            continue
        per_domain[domain] = per_domain.get(domain, 0) + 1
        if debate and debate not in ("-", "—", "–"):
            summary = f"{summary} · محل بحث: {debate}"
        items.append({"title": title, "desc": summary, "date": d.isoformat(), "source": source,
                      "domain": domain, "key": key})
    return items, sources
