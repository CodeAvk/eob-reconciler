from decimal import Decimal as D
from app.core.checks import Bill, Eob, Line, run_checks


def L(code, amt, date="2026-01-05", src=""):
    return Line(date, code, D(amt), src or f"{code}:{amt}")


def test_clean_pair_has_no_flags():
    bill = Bill([L("A", "100.00"), L("B", "50.00")], D("150.00"), D("30.00"))
    assert run_checks(bill, Eob([], D("30.00"))) == []


def test_sum_mismatch():
    bill = Bill([L("A", "100.00")], D("120.00"), D("30.00"))
    assert [f.kind for f in run_checks(bill, Eob([], D("30.00")))] == ["sum_mismatch"]


def test_duplicate_line_cites_both_sources():
    bill = Bill([L("A", "100.00", src="r1"), L("A", "100.00", src="r2")], D("200.00"), D("0"))
    flags = run_checks(bill, Eob([], D("0")))
    assert flags[0].kind == "duplicate_line" and flags[0].evidence == ("r1", "r2")


def test_eob_mismatch():
    bill = Bill([L("A", "100.00")], D("100.00"), D("80.00"))
    assert [f.kind for f in run_checks(bill, Eob([], D("30.00")))] == ["eob_mismatch"]


def test_same_code_different_date_is_not_duplicate():
    bill = Bill([L("A", "10.00", "2026-01-01"), L("A", "10.00", "2026-02-01")], D("20.00"), D("0"))
    assert run_checks(bill, Eob([], D("0"))) == []
