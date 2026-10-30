"""Non-AI baseline: OCR text rows + regular expressions.

Used by the Gate 1 evaluation as the "simple solution" Gemini must beat.
Layout-agnostic: it groups OCR boxes into rows and finds date, code and amount
anywhere in a row. It knows the synthetic code format (SYN-dddd), which is an
advantage for the baseline; real codes vary more.
"""
import io
import re
from decimal import Decimal

from app.core.checks import Bill, Eob, Line

DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
CODE = re.compile(r"SYN-\d{4}")
AMOUNT = re.compile(r"\$?\s?(\d[\d,]*\.\d{2})")
TOTAL = re.compile(r"total\s+charges", re.I)
OWES = re.compile(r"amount\s+you\s+owe", re.I)
RESPONSIBILITY = re.compile(r"your\s+responsibility", re.I)

_engine = None


def _ocr_engine():
    global _engine
    if _engine is None:
        from rapidocr import RapidOCR
        _engine = RapidOCR()
    return _engine


def ocr_rows(image_bytes: bytes, tolerance: int = 14):
    """OCR an image and return text rows (boxes grouped by vertical position)."""
    import numpy as np
    from PIL import Image
    arr = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    out = _ocr_engine()(arr)
    if out.boxes is None:
        return []
    items = sorted(((float(b[:, 1].mean()), float(b[:, 0].min()), t)
                    for b, t in zip(out.boxes, out.txts)))
    rows, current, last_y = [], [], None
    for y, x, text in items:
        if last_y is not None and abs(y - last_y) > tolerance:
            rows.append(current)
            current = []
        current.append((x, text))
        last_y = y if not current[:-1] else last_y
    if current:
        rows.append(current)
    return ["  ".join(t for _, t in sorted(r)) for r in rows]


def _amount(text):
    m = AMOUNT.search(text)
    return Decimal(m.group(1).replace(",", "")) if m else None


def parse_bill_rows(rows) -> Bill:
    lines, total, owes = [], Decimal("0"), Decimal("0")
    for row in rows:
        if TOTAL.search(row):
            total = _amount(row) or total
        elif OWES.search(row):
            owes = _amount(row) or owes
        else:
            d, c = DATE.search(row), CODE.search(row)
            amounts = AMOUNT.findall(row)
            if d and c and amounts:
                # the code's digits can be read as an amount-like token; take the last decimal amount
                lines.append(Line(d.group(), c.group(),
                                  Decimal(amounts[-1].replace(",", "")), row))
    return Bill(lines, total, owes)


def parse_eob_rows(rows) -> Eob:
    resp = Decimal("0")
    for row in rows:
        if RESPONSIBILITY.search(row):
            resp = _amount(row) or resp
    return Eob([], resp)


def extract(bill_png: bytes, eob_png: bytes):
    return parse_bill_rows(ocr_rows(bill_png)), parse_eob_rows(ocr_rows(eob_png))
