"""Gate 1 evaluation: score an extractor against synthetic ground truth.

CLI: python -m app.evaluate DATA_DIR --extractor baseline|gemini [--limit N]

Predictions are cached under data/eval/<extractor>/ so a case is never sent to
the (quota-limited) Gemini API twice.
"""
import argparse
import json
import time
from collections import Counter
from decimal import Decimal
from pathlib import Path

from app.core.checks import Bill, Eob, Line, run_checks

ROOT = Path(__file__).resolve().parents[2]


def to_models(d: dict):
    lines = [Line(l["date"], l["code"], Decimal(l["amount"]), "") for l in d["bill"]["lines"]]
    bill = Bill(lines, Decimal(d["bill"]["stated_total"]), Decimal(d["bill"]["patient_owes"]))
    return bill, Eob([], Decimal(d["eob"]["patient_responsibility"]))


def to_dict(bill: Bill, eob: Eob) -> dict:
    return {"bill": {"lines": [{"date": l.date, "code": l.code, "amount": str(l.billed)}
                               for l in bill.lines],
                     "stated_total": str(bill.stated_total),
                     "patient_owes": str(bill.patient_owes)},
            "eob": {"patient_responsibility": str(eob.patient_responsibility)}}


def _key(l: Line):
    return (l.date, l.code, l.billed)


def score_case(pred: dict, truth: dict) -> dict:
    pb, pe = to_models(pred)
    tb, te = to_models(truth)
    pc, tc = Counter(map(_key, pb.lines)), Counter(map(_key, tb.lines))
    tp = sum((pc & tc).values())
    truth_amounts = {l.billed for l in tb.lines}
    flags = sorted(f.kind for f in run_checks(pb, pe))
    expected = sorted(truth["expected_flags"])
    return {
        "line_tp": tp, "line_pred": sum(pc.values()), "line_truth": sum(tc.values()),
        "fabricated": sum(1 for l in pb.lines if l.billed not in truth_amounts),
        "total_ok": pb.stated_total == tb.stated_total,
        "owes_ok": pb.patient_owes == tb.patient_owes,
        "eob_ok": pe.patient_responsibility == te.patient_responsibility,
        "flags": flags, "expected_flags": expected, "flags_ok": flags == expected,
        "injected": truth["injected"],
    }


def aggregate(results: list) -> dict:
    ok = [r for r in results if "error" not in r]
    n = len(results)
    tp = sum(r["line_tp"] for r in ok)
    pred = sum(r["line_pred"] for r in ok)
    truth = sum(r["line_truth"] for r in results if "line_truth" in r) or 1
    prec = tp / pred if pred else 0.0
    rec = tp / truth
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    injected = [r for r in ok if r["injected"] != "none"]
    clean = [r for r in ok if r["injected"] == "none"]
    return {
        "cases": n, "errors": n - len(ok),
        "line_precision": round(prec, 3), "line_recall": round(rec, 3), "line_f1": round(f1, 3),
        "fabricated_lines": sum(r["fabricated"] for r in ok),
        "total_acc": round(sum(r["total_ok"] for r in ok) / n, 3),
        "owes_acc": round(sum(r["owes_ok"] for r in ok) / n, 3),
        "eob_acc": round(sum(r["eob_ok"] for r in ok) / n, 3),
        "flag_exact_acc": round(sum(r["flags_ok"] for r in ok) / n, 3),
        "injected_detected": f"{sum(r['injected'] in r['flags'] for r in injected)}/{len(injected)}",
        "clean_false_positives": f"{sum(bool(r['flags']) for r in clean)}/{len(clean)}",
    }


def load_cases(data_dir: Path, limit=None):
    cases = []
    for truth_path in sorted(Path(data_dir).glob("case_*_truth.json")):
        stem = truth_path.name[:-len("_truth.json")]
        cases.append((stem, truth_path.parent / f"{stem}_bill.png",
                      truth_path.parent / f"{stem}_eob.png",
                      json.loads(truth_path.read_text())))
    return cases[:limit] if limit else cases


def make_extractor(name: str, throttle: float = 0.0):
    if name == "baseline":
        from app import baseline
        return baseline.extract
    if name == "baseline_deskew":
        from app import baseline
        return baseline.extract_deskew
    if name == "gemini":
        from app import extraction

        def run(bill_png, eob_png):
            result = extraction.extract_case(bill_png, "image/png", eob_png, "image/png")
            time.sleep(throttle)
            return result
        return run
    raise SystemExit(f"unknown extractor {name}")


def evaluate(extractor, name: str, data_dir: Path, limit=None, cache_root=None):
    cache_dir = Path(cache_root or ROOT / "data" / "eval") / f"{name}_{Path(data_dir).name}"
    cache_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for stem, bill_p, eob_p, truth in load_cases(data_dir, limit):
        cache = cache_dir / f"{stem}.json"
        started = time.time()
        if cache.exists():
            pred = json.loads(cache.read_text())
        else:
            try:
                pred = to_dict(*extractor(bill_p.read_bytes(), eob_p.read_bytes()))
                pred["seconds"] = round(time.time() - started, 1)
                cache.write_text(json.dumps(pred))
            except Exception as err:  # record the failure, keep going
                results.append({"case": stem, "error": f"{type(err).__name__}: {err}",
                                "line_truth": len(truth["bill"]["lines"])})
                continue
        res = score_case(pred, truth)
        res.update(case=stem, seconds=pred.get("seconds"))
        results.append(res)
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    ap.add_argument("--extractor", choices=["baseline", "baseline_deskew", "gemini"], required=True)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--throttle", type=float, default=2.0)
    a = ap.parse_args()
    results = evaluate(make_extractor(a.extractor, a.throttle), a.extractor,
                       Path(a.data_dir), a.limit)
    report = {"extractor": a.extractor, "summary": aggregate(results), "cases": results}
    out = ROOT / "data" / "eval" / f"{a.extractor}_{Path(a.data_dir).name}_report.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["summary"], indent=2))
    for r in results:
        if "error" in r:
            print("ERROR", r["case"], r["error"])


if __name__ == "__main__":
    main()
