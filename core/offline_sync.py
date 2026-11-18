"""نسخهٔ آفلاین فقط‌خواندنی برای برنامهٔ موبایل (پوستهٔ PWA در docs/).

هر بار برنامه با اینترنت و بعد از ورود باز شود و متن‌های ذخیره‌شده تغییر کرده باشند، یک نسخهٔ سبک از آن‌ها
(تحقیق خبرها، اسکریپت‌ها، سناریو و نریشن دیپ‌دایو) با postMessage به پوستهٔ نصب‌شده فرستاده می‌شود و پوسته
آن را در حافظهٔ گوشی (IndexedDB) نگه می‌دارد. وقتی اینترنت قطع باشد، پوسته صفحهٔ خوانش آفلاین را نشان می‌دهد.

- فقط به آدرس WRAPPER_ORIGIN فرستاده می‌شود (آدرس GitHub Pages شما: https://<نام‌کاربری>.github.io).
  اگر پوسته را روی آدرس دیگری گذاشته‌اید، فقط همین یک خط را عوض کنید.
- رمزگذاری: اگر APP_PASSWORD تنظیم باشد، نسخهٔ آفلاین با AES-GCM رمز می‌شود و کلید آن از همان رمز برنامه
  (PBKDF2-SHA256) ساخته می‌شود؛ پس رمز آفلاین و آنلاین یکی است. خودِ رمز هرگز به مرورگر فرستاده نمی‌شود
  (فقط کلید مشتق‌شده، برای رمزکردن در همان لحظه). اگر APP_PASSWORD نباشد، نسخه رمزگذاری نمی‌شود.
- با عوض‌کردن رمز در Secrets، نسخهٔ آفلاین قدیمی با رمز جدید باز نمی‌شود تا یک بار با اینترنت همگام شود.
"""
import base64
import hashlib
import hmac
import json
from functools import lru_cache

import streamlit as st
import streamlit.components.v1 as components

from core.auth import _password

WRAPPER_ORIGIN = "https://mossawikian.github.io"
PBKDF2_ITER = 200_000
MAX_RESEARCH_VERSIONS = 6      # برای هر خبر فقط آخرین نسخه‌ها (حجم کم)


def build_snapshot():
    ss = st.session_state
    news = []
    for n in ss.get("news_list", []):
        research = [{"ts": v.get("ts", ""), "q": v.get("q", ""), "text": v.get("text", "")}
                    for v in (n.get("research") or [])][-MAX_RESEARCH_VERSIONS:]
        if not research and not n.get("script"):
            continue
        news.append({"title": n.get("title", ""), "status": n.get("status", ""), "week": n.get("week", ""),
                     "added": n.get("added", ""), "research": research,
                     "script": n.get("script", ""), "script_html": n.get("script_html", "")})
    deep = []
    for t in ss.get("deep_topics", []):
        if not (t.get("scenario") or t.get("narration") or t.get("narration_html")):
            continue
        deep.append({"title": t.get("title", ""), "status": t.get("status", ""), "week": t.get("week", ""),
                     "scenario": t.get("scenario", ""), "narration": t.get("narration", ""),
                     "narration_html": t.get("narration_html", "")})
    return {"v": 1, "news": news, "deep": deep}


def _js_json(obj):
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


@lru_cache(maxsize=2)
def _derive(password):
    """(salt، کلید ۳۲ بایتی) از رمز برنامه؛ salt از خود رمز ساخته می‌شود تا ذخیره‌ای لازم نباشد."""
    salt = hmac.new(password.encode("utf-8"), b"sade-offline-salt-v1", hashlib.sha256).digest()[:16]
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITER, dklen=32)
    return salt, key


def sync_offline_copy():
    """فقط وقتی محتوا تغییر کرده باشد، نسخهٔ آفلاین را به پوسته می‌فرستد."""
    ss = st.session_state
    snap = build_snapshot()
    pw = _password()
    salt, key = _derive(pw) if pw else (b"", b"")
    digest = hashlib.md5((_js_json(snap) + key.hex()).encode("utf-8")).hexdigest()
    if ss.get("_offline_hash") == digest:
        return
    ss["_offline_hash"] = digest
    msg = {"type": "sade-offline", "digest": digest, "data": snap}
    if pw:   # رمزگذاری در مرورگر انجام می‌شود؛ فقط کلید مشتق‌شده فرستاده می‌شود، نه خود رمز
        msg["key"] = key.hex()
        msg["salt"] = base64.b64encode(salt).decode()
        msg["iter"] = PBKDF2_ITER
    components.html(
        "<script>(async function(){var m=" + _js_json(msg) + ";" + _SEND_JS.replace("__ORIGIN__", json.dumps(WRAPPER_ORIGIN))
        + "})();</script>", height=0)


_SEND_JS = """
function b64(buf){var a=new Uint8Array(buf),s='';for(var i=0;i<a.length;i+=0x8000)s+=String.fromCharCode.apply(null,a.subarray(i,i+0x8000));return btoa(s);}
var out;
try{
  if(m.key){
    var raw=new Uint8Array(m.key.match(/../g).map(function(h){return parseInt(h,16);}));
    var ck=await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['encrypt']);
    var iv=crypto.getRandomValues(new Uint8Array(12));
    var ct=await crypto.subtle.encrypt({name:'AES-GCM',iv:iv},ck,new TextEncoder().encode(JSON.stringify(m.data)));
    out={type:m.type,digest:m.digest,enc:true,salt:m.salt,iter:m.iter,iv:b64(iv),ct:b64(ct)};
  }else{ out={type:m.type,digest:m.digest,enc:false,data:m.data}; }
  [window.top,window.parent].forEach(function(w){try{w.postMessage(out,__ORIGIN__);}catch(e){}});
}catch(e){}
"""
