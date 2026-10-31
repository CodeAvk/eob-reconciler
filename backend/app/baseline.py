"""Non-AI baseline: OCR text rows + regular expressions.

Used by the Gate 1 evaluation as the "simple solution" Gemini must beat.
Layout-agnostic: it groups OCR boxes into rows and finds date, code and amount
anywhere in a row. Generic patterns cover ISO, US and long dates and three code
shapes (SYN-dddd, letter+4 digits, 5 digits). One bounded round of tuning was
done after the easy-set run; it was not tuned against individual failures.
"""
import io
import re
from decimal import Decimal

from app.core.checks import Bill, Eob, Line

DATE = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|[A-Z][a-z]{2} \d{1,2}, \d{4}")
CODE = re.compile(r"\bSYN-\d{4}\b|\b[A-Z]\d{4}\b|\b\d{5}\b")
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


def tilt_degrees(boxes) -> float:
    """Median angle of OCR box top edges, in degrees (page tilt)."""
    import math
    import statistics
    angles = [math.degrees(math.atan2(b[1][1] - b[0][1], b[1][0] - b[0][0])) for b in boxes]
    return statistics.median(angles) if angles else 0.0


def group_rows(items, tolerance: int):
    """items: (y, x, text). Group into rows by vertical position, then sort by x."""
    rows, current, anchor = [], [], None
    for y, x, text in sorted(items):
        if anchor is not None and abs(y - anchor) > tolerance:
            rows.append(current)
            current, anchor = [], None
        current.append((x, text))
        anchor = y if anchor is None else anchor
    if current:
        rows.append(current)
    return ["  ".join(t for _, t in sorted(r)) for r in rows]


def ocr_rows(image_bytes: bytes, tolerance: int = 22, deskew: bool = False):
    """OCR an image and return text rows. With deskew, box centres are rotated
    back by the measured page tilt before rows are grouped."""
    import math

    import numpy as np
    from PIL import Image
    arr = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    out = _ocr_engine()(arr)
    if out.boxes is None:
        return []
    theta = math.radians(tilt_degrees(out.boxes)) if deskew else 0.0
    cos, sin = math.cos(-theta), math.sin(-theta)
    items = []
    for box, text in zip(out.boxes, out.txts):
        cx, cy = float(box[:, 0].mean()), float(box[:, 1].mean())
        x, y = cx * cos - cy * sin, cx * sin + cy * cos
        items.append((y, x, text))
    return group_rows(items, 14 if deskew else tolerance)


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


def extract(bill_png: bytes, eob_png: bytes, deskew: bool = False):
    return (parse_bill_rows(ocr_rows(bill_png, deskew=deskew)),
            parse_eob_rows(ocr_rows(eob_png, deskew=deskew)))


def extract_deskew(bill_png: bytes, eob_png: bytes):
    """Stronger baseline: the same OCR + regex, with page-tilt correction."""
    return extract(bill_png, eob_png, deskew=True)
