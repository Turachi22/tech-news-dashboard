"""وضعیت مصرف روزانه، فهرست مدل‌ها، کلیدها و کنار گذاشتن موقت مدل‌ها/کلیدهای بی‌سهمیه."""
import datetime as dt
import re
import time
from zoneinfo import ZoneInfo

import streamlit as st
from google import genai

from core.ai.config import ALLOW_FALLBACK, PREFERRED_MODELS


@st.cache_resource
def _usage():
    return {"day": "", "count": 0}


def _today_pt():
    return dt.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")


def usage_today():
    u = _usage()
    if u["day"] != _today_pt():
        u["day"], u["count"] = _today_pt(), 0
    return u["count"]


def _count_request():
    usage_today()
    _usage()["count"] += 1


@st.cache_resource
def _blocked():
    """مدل‌هایی که موقتاً (به‌خاطر سهمیه) کنار گذاشته شده‌اند: نام مدل -> زمان آزاد شدن."""
    return {}


@st.cache_data(ttl=3600, show_spinner=False)
def _list_models(api_key):
    client = genai.Client(api_key=api_key)
    return [m.name for m in client.models.list()
            if "generateContent" in (getattr(m, "supported_actions", None) or [])]


def _version(name):
    m = re.search(r"gemini-(\d+(?:\.\d+)?)", name)
    return float(m.group(1)) if m else 0.0


def _discover(api_key):
    """مدل‌های flash متنی حساب شما، از جدیدترین نسخه به قدیمی‌ترین (فقط برای ALLOW_FALLBACK)."""
    skip = ("image", "tts", "live", "embedding", "audio", "exp", "vision", "robotics",
            "omni", "computer", "native", "pro")
    flash = [n.replace("models/", "") for n in _list_models(api_key)
             if ("flash" in n or "gemma" in n) and not any(x in n for x in skip)]
    flash.sort(key=lambda n: ("gemma" in n, _version(n) < 3, "latest" in n, -_version(n), "lite" in n, "preview" in n, n))
    return flash


def _candidates(api_key):
    """مدل‌های PREFERRED_MODELS که واقعاً در حساب شما وجود دارند (بدون صرف درخواست)؛
    اگر هیچ‌کدام نبود، یا ALLOW_FALLBACK روشن بود، مدل‌های flash دیگر هم اضافه می‌شوند."""
    models = list(PREFERRED_MODELS)
    discovered = []
    try:
        discovered = _discover(api_key)
        available = set(discovered) | {n.replace("models/", "") for n in _list_models(api_key)}
        models = [m for m in models if m in available]
    except Exception:  # noqa: BLE001  (فهرست در دسترس نبود؛ همان فهرست ترجیحی را نگه می‌داریم)
        pass
    if ALLOW_FALLBACK:
        models += [n for n in discovered if n not in models]
    return models


@st.cache_resource
def _reasons():
    return {}


def _brief(exc):
    """خلاصهٔ خطا: کد، نام سهمیه‌ای که تمام شده و سقف آن."""
    t = str(exc)
    ids = list(dict.fromkeys(re.findall(r"quotaId['\"]?: ?['\"]?([\w-]+)", t)))
    lim = list(dict.fromkeys(re.findall(r"limit: (\d+)", t)))
    out = t[:160].replace("\n", " ")
    if ids:
        out += " | " + ", ".join(ids)
    if lim:
        out += " | limit=" + ",".join(lim)
    return out


def _code(low, c):
    return re.search(rf"\b{c}\b", low) is not None


def _is_quota(low):
    return _code(low, "429") or "resource_exhausted" in low or "quota" in low


def _get_keys():
    """کلیدها را از Secrets (برای استقرار) و از کادرهای منوی کناری جمع می‌کند."""
    keys = []
    try:
        sec = st.secrets.get("GEMINI_API_KEYS") or st.secrets.get("GEMINI_API_KEY")
        if isinstance(sec, str):
            keys.append(sec)
        elif sec:
            keys.extend(sec)
    except Exception:  # noqa: BLE001  (فایل secrets وجود ندارد)
        pass
    keys += [st.session_state.get("api_key", ""), st.session_state.get("api_key2", "")]
    out = []
    for k in keys:
        k = (k or "").strip()
        if k and k not in out:
            out.append(k)
    return out


def _is_blocked(kid, name):
    b, now = _blocked(), time.time()
    return max(b.get(f"{kid}:*", 0), b.get(f"{kid}:{name}", 0)) > now


def _block(kid, name, exc):
    """بر اساس نوع خطا تعیین می‌کند این (کلید، مدل) تا چه زمانی کنار بماند."""
    low = str(exc).lower()
    _reasons()[f"{kid}:{name}"] = _brief(exc)
    if any(w in low for w in ("api_key_invalid", "api key not valid", "permission_denied")) or _code(low, "403"):
        _blocked()[f"{kid}:*"] = time.time() + 3600  # کلید نامعتبر
        return
    if "limit: 0" in low or _code(low, "404") or any(w in low for w in ("no longer available", "not found")):
        secs = 24 * 3600  # در پلن رایگان وجود ندارد
    elif "perday" in low.replace(" ", "") or "per day" in low:
        tz = ZoneInfo("America/Los_Angeles")  # سهمیهٔ روزانه نیمه‌شب وقت لس‌آنجلس ریست می‌شود
        now = dt.datetime.now(tz)
        nxt = (now + dt.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        secs = (nxt - now).total_seconds()
    elif _code(low, "503") or "unavailable" in low or "high demand" in low:
        secs = 30  # شلوغی موقت سرور گوگل؛ زود دوباره امتحان می‌شود
    else:
        m = re.search(r"retry in ([\d.]+)s", low)
        secs = min(float(m.group(1)) if m else 60, 300) + 3  # سقف دقیقه‌ای
    _blocked()[f"{kid}:{name}"] = time.time() + secs


