"""ویرایشگر متن غنی (رنگ و اندازه، مثل Word) برای «ویرایش نریشن دیپ‌دایو» و «اسکریپت اخبار».

- ویرایشگر یک کامپوننت محلی است (components/rich_editor/index.html)؛ بدون نصب هیچ بسته‌ای.
- متن به‌صورت HTML ذخیره می‌شود و همیشه قبل از ذخیره و نمایش پاک‌سازی می‌شود (فقط رنگ، اندازه، پررنگ، خط‌شکنی).
- نسخهٔ متن ساده هم کنار آن نگه داشته می‌شود (برای خروجی متنی).
"""
import html as _html
import re
import uuid
from html.parser import HTMLParser
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as stc

_DIR = Path(__file__).resolve().parent.parent / "components" / "rich_editor"
_comp = stc.declare_component("sade_rich_editor", path=str(_DIR))

_TAGS = {"span", "b", "strong", "i", "em", "u", "br", "div", "p", "font"}
_SKIP = {"script", "style", "iframe", "object", "embed"}
_BLOCK = {"div", "p"}
_COLOR = re.compile(r"^(#[0-9a-fA-F]{3,8}|rgba?\([\d\s,.%]+\)|[a-zA-Z]{3,20})$")
_SIZE = re.compile(r"^\d{1,3}(\.\d+)?(px|pt)$")
_KEYWORD_PX = {"xx-small": 9, "x-small": 10, "small": 13, "medium": 16, "large": 18,
               "x-large": 24, "xx-large": 32, "xxx-large": 48}


def new_uid():
    return uuid.uuid4().hex[:8]


def _clean_style(style):
    out = []
    for decl in (style or "").split(";"):
        if ":" not in decl:
            continue
        k, v = (x.strip() for x in decl.split(":", 1))
        k = k.lower()
        if k in ("color", "background-color") and _COLOR.match(v):
            out.append(f"{k}:{v}")
        elif k == "font-size":
            if v in _KEYWORD_PX:
                v = f"{_KEYWORD_PX[v]}px"
            if _SIZE.match(v):
                out.append(f"font-size:{v}")
        elif k == "font-weight" and v in ("bold", "normal", "500", "600", "700", "800"):
            out.append(f"font-weight:{v}")
        elif k == "font-style" and v in ("italic", "normal"):
            out.append(f"font-style:{v}")
        elif k == "text-decoration" and v in ("underline", "none"):
            out.append(f"text-decoration:{v}")
    return ";".join(out)


class _Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP:
            self.skip += 1
            return
        if self.skip or tag not in _TAGS:
            return
        a = dict(attrs)
        style = _clean_style(a.get("style", ""))
        if tag == "font":                       # <font color size> قدیمی مرورگر → span
            if a.get("color") and _COLOR.match(a["color"]):
                style = f"color:{a['color']};" + style
            tag = "span"
        self.out.append(f"<{tag}" + (f' style="{style}"' if style and tag != "br" else "") + (" />" if tag == "br" else ">"))

    def handle_endtag(self, tag):
        if tag in _SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag not in _TAGS or tag == "br":
            return
        self.out.append("</span>" if tag == "font" else f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(_html.escape(data))


def sanitize(html):
    p = _Sanitizer()
    p.feed(html or "")
    p.close()
    return "".join(p.out)


class _Runs(HTMLParser):
    """HTML پاک‌سازی‌شده → پاراگراف‌ها و ران‌ها (متن، رنگ، اندازهٔ px، پررنگ)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paras, self.cur, self.stack = [], [], [{}]

    def _brk(self, force=False):
        if self.cur or force:
            self.paras.append(self.cur)
            self.cur = []

    def handle_starttag(self, tag, attrs):
        fmt = dict(self.stack[-1])
        if tag in ("b", "strong"):
            fmt["bold"] = True
        if tag in ("i", "em"):
            fmt["italic"] = True
        style = dict(attrs).get("style", "")
        for decl in style.split(";"):
            if ":" not in decl:
                continue
            k, v = (x.strip() for x in decl.split(":", 1))
            if k == "color":
                fmt["color"] = v
            elif k == "font-size":
                m = re.match(r"([\d.]+)(px|pt)", v)
                if m:
                    fmt["size"] = float(m.group(1)) * (1 if m.group(2) == "px" else 4 / 3)
            elif k == "font-weight" and v in ("bold", "600", "700", "800"):
                fmt["bold"] = True
        if tag in _BLOCK:
            self._brk()
        if tag == "br":
            self._brk(force=True)
        self.stack.append(fmt)

    def handle_endtag(self, tag):
        if len(self.stack) > 1:
            self.stack.pop()
        if tag in _BLOCK:
            self._brk()

    def handle_data(self, data):
        if data.strip("\n") != "" or data == " ":
            self.cur.append((data.replace("\n", " "), dict(self.stack[-1])))


def html_to_paragraphs(html):
    p = _Runs()
    p.feed(sanitize(html))
    p.close()
    p._brk()
    return p.paras


def html_to_text(html):
    return "\n".join("".join(t for t, _f in para) for para in html_to_paragraphs(html)).strip("\n")


def md_to_html(text):
    """متن ساده یا مارک‌داون سادهٔ قبلی → HTML برای ویرایشگر (هر خط یک div؛ **پررنگ** و *مورب*)."""
    lines = []
    for ln in (text or "").splitlines():
        h = _html.escape(ln)
        h = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", h)
        h = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<i>\1</i>", h)
        lines.append(f"<div>{h}</div>" if h.strip() else "<div><br></div>")
    return "".join(lines)


def rich_editor(html, key, height=360):
    """ویرایشگر؛ فقط وقتی کاربر «ذخیره» بزند دیکشنری {html, t} برمی‌گرداند، وگرنه None.
    key باید شناسهٔ پایدار آیتم + نسخه باشد (نه شمارهٔ ردیف)، وگرنه بعد از حذف یک آیتم، مقدار آیتم دیگر نشت می‌کند."""
    return _comp(html=html, height=height, key=key, default=None)


def show(html):
    """نمایش HTML پاک‌سازی‌شده (راست‌به‌چپ)."""
    body = f'<div dir="rtl" style="line-height:2;font-size:16px">{sanitize(html)}</div>'
    if hasattr(st, "html"):
        st.html(body)
    else:  # نسخه‌های قدیمی Streamlit
        st.markdown(body, unsafe_allow_html=True)
