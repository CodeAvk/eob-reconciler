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


def test_extract_case_uses_one_request_with_two_images():
    from app.extraction import extract_case
    calls = []

    def fake(prompt, **kw):
        calls.append(kw)
        return {"bill": {"lines": [{"date": "d", "code": "A", "amount": "5.00", "source": "r"}],
                         "stated_total": "5.00", "patient_owes": "1.00"},
                "eob": {"patient_responsibility": "1.00"}}

    bill, eob = extract_case(b"b", "image/png", b"e", "image/jpeg", fake)
    assert len(calls) == 1 and len(calls[0]["images"]) == 2
    assert bill.stated_total == D("5.00") and eob.patient_responsibility == D("1.00")
