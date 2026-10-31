import json
from decimal import Decimal as D

from app.baseline import parse_bill_rows, parse_eob_rows
from app.core.checks import Bill, Eob, Line
from app.evaluate import aggregate, evaluate, score_case, to_dict
from app.synthetic import generate


def test_parse_bill_rows_handles_layouts():
    rows = ["Sample Clinic B", "Date  Code  Description  Amount",
            "2026-03-21  SYN-5856  Therapy session  $178.45",
            "$573.26  2026-06-24  SYN-9205  Consultation",
            "Total charges: $751.71", "Amount you owe: $279.05"]
    bill = parse_bill_rows(rows)
    assert [(l.code, l.billed) for l in bill.lines] == [("SYN-5856", D("178.45")),
                                                         ("SYN-9205", D("573.26"))]
    assert bill.stated_total == D("751.71") and bill.patient_owes == D("279.05")


def test_parse_eob_rows():
    assert parse_eob_rows(["Plan paid: $1.00", "Your responsibility: $1,200.50"]) \
        .patient_responsibility == D("1200.50")


def _truth(lines, total, owes, eob, injected="none", flags=()):
    pred = to_dict(Bill([Line(*l, "") for l in lines], D(total), D(owes)), Eob([], D(eob)))
    return {**pred, "injected": injected, "expected_flags": list(flags)}


def test_score_perfect_and_wrong_prediction():
    truth = _truth([("2026-01-01", "SYN-1", D("10.00"))], "10.00", "2.00", "2.00")
    perfect = score_case({k: truth[k] for k in ("bill", "eob")}, truth)
    assert perfect["line_tp"] == 1 and perfect["flags_ok"] and perfect["fabricated"] == 0
    wrong = _truth([("2026-01-01", "SYN-1", D("99.00"))], "10.00", "2.00", "2.00")
    r = score_case({k: wrong[k] for k in ("bill", "eob")}, truth)
    assert r["line_tp"] == 0 and r["fabricated"] == 1 and not r["flags_ok"]


def test_aggregate_counts_errors_against_recall():
    ok = {"line_tp": 1, "line_pred": 1, "line_truth": 1, "fabricated": 0, "total_ok": True,
          "owes_ok": True, "eob_ok": True, "flags": [], "expected_flags": [],
          "flags_ok": True, "injected": "none"}
    summary = aggregate([ok, {"case": "x", "error": "boom", "line_truth": 1}])
    assert summary["errors"] == 1 and summary["line_recall"] == 0.5
    assert summary["clean_false_positives"] == "0/1"


def test_evaluate_uses_cache_and_survives_errors(tmp_path):
    generate(tmp_path / "data", count=2, seed=1)
    calls = []

    def fake(bill_png, eob_png):
        calls.append(1)
        truth = json.loads(next((tmp_path / "data").glob("case_000_truth.json")).read_text())
        from app.evaluate import to_models
        if len(calls) == 2:
            raise RuntimeError("quota")
        return to_models(truth)

    cache = tmp_path / "cache"
    first = evaluate(fake, "fake", tmp_path / "data", cache_root=cache)
    assert "error" not in first[0] and "error" in first[1]
    evaluate(fake, "fake", tmp_path / "data", cache_root=cache)
    assert len(calls) == 3  # case 0 came from cache, only the failed case retried


def test_parse_bill_rows_other_formats_and_distractors():
    rows = ["Aug 15, 2026  B4025  Physical therapy  $2,703.87",
            "03/04/2026  49767  Follow-up  $763.41",
            "May 16, 2026  Payment received  -$227.07",
            "Total charges: $3,467.28", "Amount you owe: $100.00"]
    bill = parse_bill_rows(rows)
    assert [(l.code, l.billed) for l in bill.lines] == [("B4025", D("2703.87")),
                                                         ("49767", D("763.41"))]
    assert bill.stated_total == D("3467.28")


def test_group_rows_orders_by_x_and_splits_on_y():
    from app.baseline import group_rows
    items = [(100.0, 300.0, "B"), (101.0, 50.0, "A"), (160.0, 10.0, "C")]
    assert group_rows(items, 14) == ["A  B", "C"]


def test_tilt_degrees_measures_median_top_edge_angle():
    import math
    import numpy as np
    from app.baseline import tilt_degrees
    t = math.radians(2.0)
    box = np.array([[0, 0], [100 * math.cos(t), 100 * math.sin(t)], [100, 20], [0, 20]])
    assert abs(tilt_degrees([box, box, box]) - 2.0) < 0.01
    assert tilt_degrees([]) == 0.0
