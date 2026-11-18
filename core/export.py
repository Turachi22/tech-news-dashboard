"""خروجی Word (.docx) راست‌به‌چپ. اگر python-docx نصب نباشد، HAS_DOCX برابر False می‌شود."""
import io

try:
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    HAS_DOCX = True
except Exception:  # noqa: BLE001
    HAS_DOCX = False

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
FONT = "Tahoma"


def _para(doc, text, bold=False, size=12):
    p = doc.add_paragraph()
    p._p.get_or_add_pPr().append(OxmlElement("w:bidi"))  # پاراگراف راست‌به‌چپ
    r = p.add_run(text)
    rpr = r._r.get_or_add_rPr()
    for child in list(rpr):
        rpr.remove(child)
    fonts = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        fonts.set(qn(attr), FONT)
    rpr.append(fonts)
    if bold:
        rpr.append(OxmlElement("w:b"))
        rpr.append(OxmlElement("w:bCs"))
    for tag in ("w:sz", "w:szCs"):
        el = OxmlElement(tag)
        el.set(qn("w:val"), str(int(size * 2)))
        rpr.append(el)
    rpr.append(OxmlElement("w:rtl"))
    return p


def _rich_para(doc, runs, default_size=12):
    """یک پاراگراف با ران‌های رنگی/اندازه‌دار؛ runs: [(متن، {color, size(px), bold})]."""
    p = doc.add_paragraph()
    p._p.get_or_add_pPr().append(OxmlElement("w:bidi"))
    for text, fmt in runs or [("", {})]:
        r = p.add_run(text)
        rpr = r._r.get_or_add_rPr()
        for child in list(rpr):
            rpr.remove(child)
        fonts = OxmlElement("w:rFonts")
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            fonts.set(qn(attr), FONT)
        rpr.append(fonts)
        if fmt.get("bold"):
            rpr.append(OxmlElement("w:b"))
            rpr.append(OxmlElement("w:bCs"))
        col = _hex(fmt.get("color"))
        if col:
            c = OxmlElement("w:color")
            c.set(qn("w:val"), col)
            rpr.append(c)
        pt = round(fmt["size"] * 0.75) if fmt.get("size") else default_size
        for tag in ("w:sz", "w:szCs"):
            el = OxmlElement(tag)
            el.set(qn("w:val"), str(int(pt * 2)))
            rpr.append(el)
        rpr.append(OxmlElement("w:rtl"))
    return p


def _hex(color):
    """#rrggbb یا rgb(r,g,b) → «RRGGBB» (یا None)."""
    if not color:
        return None
    import re
    m = re.match(r"^#([0-9a-fA-F]{6})$", color.strip())
    if m:
        return m.group(1).upper()
    m = re.match(r"^#([0-9a-fA-F]{3})$", color.strip())
    if m:
        return "".join(ch * 2 for ch in m.group(1)).upper()
    m = re.match(r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", color)
    if m:
        return "".join(f"{min(255, int(x)):02X}" for x in m.groups())
    return None


def make_docx(sections):
    """sections: فهرستی از (عنوان، توضیح کوتاه، متن). خروجی: bytes فایل Word."""
    doc = Document()
    for i, sec in enumerate(sections):
        title, meta, body = sec[:3]
        html = sec[3] if len(sec) > 3 else ""
        if i:
            doc.add_page_break()
        _para(doc, title, bold=True, size=16)
        if meta:
            _para(doc, meta, size=10)
        _para(doc, "")
        if html:
            from core.richtext import html_to_paragraphs
            for runs in html_to_paragraphs(html) or [[]]:
                _rich_para(doc, runs)
        else:
            for line in (body or "").splitlines() or [""]:
                _para(doc, line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
