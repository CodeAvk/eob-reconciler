"""Deterministic bill-vs-EOB checks. No AI here: extraction feeds this module,
and every flag cites the line(s) it came from."""
from dataclasses import dataclass, field
from decimal import Decimal

CENT = Decimal("0.01")


@dataclass(frozen=True)
class Line:
    date: str
    code: str
    billed: Decimal
    source: str = ""


@dataclass
class Bill:
    lines: list
    stated_total: Decimal
    patient_owes: Decimal


@dataclass
class Eob:
    lines: list
    patient_responsibility: Decimal


@dataclass(frozen=True)
class Flag:
    kind: str
    message: str
    evidence: tuple = field(default_factory=tuple)


def check_sum(bill: Bill):
    total = sum((l.billed for l in bill.lines), Decimal("0"))
    if abs(total - bill.stated_total) >= CENT:
        return [Flag("sum_mismatch",
                     f"Line items sum to {total} but bill states {bill.stated_total}",
                     tuple(l.source for l in bill.lines))]
    return []


def check_duplicates(bill: Bill):
    seen, flags = {}, []
    for l in bill.lines:
        key = (l.date, l.code, l.billed)
        if key in seen:
            flags.append(Flag("duplicate_line",
                              f"Code {l.code} on {l.date} for {l.billed} appears more than once",
                              (seen[key].source, l.source)))
        else:
            seen[key] = l
    return flags


def check_patient_amount(bill: Bill, eob: Eob):
    if abs(bill.patient_owes - eob.patient_responsibility) >= CENT:
        return [Flag("eob_mismatch",
                     f"Bill asks patient for {bill.patient_owes}; EOB patient responsibility is "
                     f"{eob.patient_responsibility}")]
    return []


def run_checks(bill: Bill, eob: Eob):
    return check_sum(bill) + check_duplicates(bill) + check_patient_amount(bill, eob)
