"""ابزار شباهت متن (حذف موضوع‌های تکراری)."""
import re


def _words(text):
    return {w for w in re.sub(r"[^\w\s]", " ", str(text).lower().replace("\u200c", " ")).split() if len(w) > 1}


def _similar(a, b, thr=0.5):
    wa, wb = _words(a), _words(b)
    return bool(wa and wb) and len(wa & wb) / len(wa | wb) >= thr
