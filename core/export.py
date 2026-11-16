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


def make_docx(sections):
    """sections: فهرستی از (عنوان، توضیح کوتاه، متن). خروجی: bytes فایل Word."""
    doc = Document()
    for i, (title, meta, body) in enumerate(sections):
        if i:
            doc.add_page_break()
        _para(doc, title, bold=True, size=16)
        if meta:
            _para(doc, meta, size=10)
        _para(doc, "")
        for line in (body or "").splitlines() or [""]:
            _para(doc, line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
