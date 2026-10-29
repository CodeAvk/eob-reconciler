from decimal import Decimal as D

import pytest

from app.extraction import ExtractionError, extract_bill, extract_eob


def test_extract_bill_parses_amounts():
    fake = lambda *a, **k: {"lines": [{"date": "2026-01-01", "code": " A1 ",
                                       "amount": "$1,200.50", "source": "row"}],
                            "stated_total": "1,200.50", "patient_owes": "20"}
    bill = extract_bill(b"x", "image/png", fake)
    assert bill.lines[0].billed == D("1200.50") and bill.lines[0].code == "A1"
    assert bill.patient_owes == D("20")


def test_bad_amount_raises():
    with pytest.raises(ExtractionError):
        extract_eob(b"x", "image/png", lambda *a, **k: {"patient_responsibility": "n/a"})
