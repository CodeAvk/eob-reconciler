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
