import json
import random

import pytest

from app.synthetic import ERRORS, expected_flags, generate, make_case


@pytest.mark.parametrize("injected", ERRORS)
def test_injected_error_is_the_only_flag(injected):
    for seed in range(20):
        case = make_case(random.Random(seed), injected)
        want = [] if injected is None else [injected]
        assert expected_flags(case) == want, (seed, injected)


def test_deterministic_for_same_seed():
    a = make_case(random.Random(5), "sum_mismatch")
    b = make_case(random.Random(5), "sum_mismatch")
    assert a.bill == b.bill and a.eob == b.eob


def test_codes_are_not_real_cpt():
    case = make_case(random.Random(1))
    assert all(l.code.startswith("SYN-") for l in case.bill.lines)


def test_generate_writes_images_and_truth(tmp_path):
    assert generate(tmp_path, count=4, seed=3) == 4
    assert len(list(tmp_path.glob("*_bill.png"))) == 4
    truth = json.loads((tmp_path / "case_001_truth.json").read_text())
    assert truth["injected"] == "sum_mismatch" and truth["expected_flags"] == ["sum_mismatch"]


@pytest.mark.parametrize("injected", ERRORS)
def test_hard_mode_keeps_exact_ground_truth(injected):
    for seed in range(15):
        case = make_case(random.Random(seed), injected, hard=True)
        want = [] if injected is None else [injected]
        assert expected_flags(case) == want, (seed, injected)
        assert case.hard and case.extra  # distractor rows present


def test_hard_mode_varies_formats():
    dates, codes = set(), set()
    for seed in range(40):
        case = make_case(random.Random(seed), None, hard=True)
        dates.update("/" in l.date or "," in l.date for l in case.bill.lines)
        codes.update(l.code.startswith("SYN-") for l in case.bill.lines)
    assert dates == {True, False} and codes == {True, False}


def test_hard_images_render(tmp_path):
    assert generate(tmp_path, count=4, seed=2, hard=True) == 4
    truth = json.loads((tmp_path / "case_000_truth.json").read_text())
    assert truth["hard"] is True
