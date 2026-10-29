"""Gemini-backed extraction of bill / EOB line items into the check models.

The model is told to copy only what is printed. Each line carries the printed
row text as `source` so every downstream flag can cite evidence.
"""
from decimal import Decimal, InvalidOperation

from app.core import gemini_client
from app.core.checks import Bill, Eob, Line

_LINE = {"type": "OBJECT", "properties": {
    "date": {"type": "STRING"}, "code": {"type": "STRING"},
    "amount": {"type": "STRING"}, "source": {"type": "STRING"}},
    "required": ["date", "code", "amount", "source"]}

BILL_SCHEMA = {"type": "OBJECT", "properties": {
    "lines": {"type": "ARRAY", "items": _LINE},
    "stated_total": {"type": "STRING"}, "patient_owes": {"type": "STRING"}},
    "required": ["lines", "stated_total", "patient_owes"]}

EOB_SCHEMA = {"type": "OBJECT", "properties": {
    "patient_responsibility": {"type": "STRING"}},
    "required": ["patient_responsibility"]}

_RULES = ("Copy values exactly as printed. Never infer, correct or calculate. "
          "Amounts are plain decimals without currency symbols or commas. "
          "If a value is not printed, return 0.00.")


class ExtractionError(ValueError):
    pass


def _money(value: str) -> Decimal:
    try:
        return Decimal(str(value).replace("$", "").replace(",", "").strip())
    except InvalidOperation:
        raise ExtractionError(f"Not a valid amount: {value!r}") from None


def extract_bill(image: bytes, mime: str, generate=gemini_client.generate) -> Bill:
    data = generate("Extract the itemized provider bill. " + _RULES,
                    image_bytes=image, mime_type=mime, schema=BILL_SCHEMA)
    lines = [Line(l["date"], l["code"].strip(), _money(l["amount"]), l["source"])
             for l in data["lines"]]
    return Bill(lines, _money(data["stated_total"]), _money(data["patient_owes"]))


def extract_eob(image: bytes, mime: str, generate=gemini_client.generate) -> Eob:
    data = generate("Extract the patient responsibility amount from this "
                    "explanation of benefits. " + _RULES,
                    image_bytes=image, mime_type=mime, schema=EOB_SCHEMA)
    return Eob([], _money(data["patient_responsibility"]))
