"""Process one case: load files, extract with AI, run deterministic checks."""
from dataclasses import asdict

from app import extraction
from app.core.checks import run_checks
from app.repo import now


def _line(l):
    return {"date": l.date, "code": l.code, "amount": str(l.billed), "source": l.source}


def process_case(case_id, repo, storage, extract=extraction.extract_case):
    case = repo.get(case_id)
    repo.update(case_id, {"status": "processing", "updated_at": now()})
    try:
        bill, eob = extract(storage.get(case["bill_key"]), case["bill_mime"],
                            storage.get(case["eob_key"]), case["eob_mime"])
        flags = [asdict(f) for f in run_checks(bill, eob)]
        repo.update(case_id, {
            "status": "done", "updated_at": now(), "error": None, "flags": flags,
            "bill": {"lines": [_line(l) for l in bill.lines],
                     "stated_total": str(bill.stated_total),
                     "patient_owes": str(bill.patient_owes)},
            "eob": {"patient_responsibility": str(eob.patient_responsibility)},
        })
    except Exception as err:  # surface any failure on the case, never lose it
        repo.update(case_id, {"status": "failed", "updated_at": now(),
                              "error": f"{type(err).__name__}: {err}"})
