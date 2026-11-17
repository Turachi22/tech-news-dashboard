"""جست‌وجوی وب با Groq (groq/compound) — بدون کتابخانهٔ اضافه (فقط urllib).

Groq فقط «جست‌وجو و جمع‌آوری منبع» را انجام می‌دهد؛ نوشتن متن فارسی با Gemini است.
کلید در Streamlit Secrets با نام GROQ_API_KEY گذاشته می‌شود. اگر کلید نباشد یا Groq خطا بدهد،
برنامه خودکار به مسیر قبلی (Gemini) برمی‌گردد.
"""
import json
import time
import urllib.error
import urllib.request

import streamlit as st

URL = "https://api.groq.com/openai/v1/chat/completions"
MODELS = ["groq/compound", "groq/compound-mini"]   # اگر اولی خطا داد، دومی
TIMEOUT = 120
SYSTEM = ("You are a careful web research assistant. Use web search. Report only what you actually found in "
          "sources; never invent facts, dates or links. Always name the source of each claim.")


class GroqError(Exception):
    def __init__(self, msg, code=0, retry_after=None):
        super().__init__(msg)
        self.code = code
        self.retry_after = retry_after


@st.cache_resource
def _state():
    return {"until": 0.0, "why": ""}


def groq_key():
    try:
        return str(st.secrets.get("GROQ_API_KEY", "") or "").strip()
    except Exception:  # noqa: BLE001
        return ""


def available():
    """کلید هست و Groq موقتاً (به‌خاطر سقف) کنار گذاشته نشده است."""
    return bool(groq_key()) and time.time() >= _state()["until"]


def blocked_info():
    s = _state()
    return (s["why"], max(int(s["until"] - time.time()), 0)) if time.time() < s["until"] else ("", 0)


def _post(body, key):
    req = urllib.request.Request(
        URL, data=json.dumps(body).encode("utf-8"), method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "User-Agent": "sade-dashboard/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500].replace("\n", " ")
        raise GroqError(f"HTTP {e.code}: {detail}", e.code, e.headers.get("retry-after")) from e
    except Exception as e:  # noqa: BLE001  (شبکه، timeout، JSON خراب)
        raise GroqError(f"{type(e).__name__}: {str(e)[:200]}") from e


def _sources(message):
    """لینک‌ها و خلاصهٔ محتوای نتایج جست‌وجو از executed_tools؛ {url: {title, content}}."""
    out = {}
    for tool in message.get("executed_tools") or []:
        sr = (tool or {}).get("search_results") or {}
        results = sr.get("results") if isinstance(sr, dict) else sr
        for r in results or []:
            if isinstance(r, dict) and r.get("url"):
                out.setdefault(r["url"], {"title": (r.get("title") or r["url"]).strip(),
                                          "content": (r.get("content") or "").strip()})
    return out


def _block(exc):
    msg = str(exc).lower()
    if exc.code == 429:
        if "per day" in msg or "tokens per day" in msg or "requests per day" in msg:
            secs = 3600
        else:
            try:
                secs = min(float(exc.retry_after), 300)
            except (TypeError, ValueError):
                secs = 60
        _state().update(until=time.time() + secs, why="سقف Groq")
    elif exc.code in (401, 403):
        _state().update(until=time.time() + 3600, why="کلید Groq نامعتبر یا بدون دسترسی")


def search(prompt):
    """یک جست‌وجو. خروجی: (متن یافته‌ها، {url: {title, content}}). در خطا GroqError."""
    key = groq_key()
    if not key:
        raise GroqError("GROQ_API_KEY تنظیم نشده است")
    if time.time() < _state()["until"]:
        raise GroqError(f"Groq موقتاً کنار گذاشته شده ({_state()['why']})")
    last = None
    for model in MODELS:
        body = {"model": model, "temperature": 0.3,
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                "compound_custom": {"tools": {"enabled_tools": ["web_search"]}}}
        try:
            try:
                data = _post(body, key)
            except GroqError as e:
                if e.code != 400:
                    raise
                body.pop("compound_custom")      # اگر این پارامتر پذیرفته نشد، بدونش
                data = _post(body, key)
            msg = (data.get("choices") or [{}])[0].get("message") or {}
            text = (msg.get("content") or "").strip()
            if not text:
                raise GroqError("پاسخ خالی از Groq")
            return text, _sources(msg)
        except GroqError as e:
            last = e
            if e.code in (0, 404, 429, 500, 502, 503):
                continue      # مدل بعدی (compound-mini)
            break
    _block(last)
    raise last


def ping():
    """تست سریع برای صفحهٔ تنظیمات: (True/False، توضیح)."""
    key = groq_key()
    if not key:
        return False, "GROQ_API_KEY در Secrets نیست"
    try:
        data = _post({"model": MODELS[1], "max_tokens": 5,
                      "messages": [{"role": "user", "content": "Reply with: OK"}]}, key)
        return True, (data["choices"][0]["message"].get("content") or "").strip()[:40]
    except GroqError as e:
        return False, str(e)[:400]
