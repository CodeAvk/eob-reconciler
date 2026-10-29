"""Synthetic bill / EOB generator with known ground truth.

Everything is fictional: provider names, codes (opaque SYN-xxxx strings, not
real CPT codes) and amounts. Each case can inject one known error so that
extraction and checks can be scored against exact expectations.

CLI: python -m app.synthetic OUT_DIR [COUNT] [SEED]
"""
import json
import random
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.core.checks import Bill, Eob, Line, run_checks

ERRORS = (None, "sum_mismatch", "duplicate_line", "eob_mismatch")
DESCRIPTIONS = ("Office visit", "Lab panel", "Imaging study", "Procedure supplies",
                "Consultation", "Therapy session", "Facility fee")
FONT_FILES = ("arial.ttf", "calibri.ttf", "segoeui.ttf")


@dataclass
class Case:
    bill: Bill
    eob: Eob
    descriptions: list
    provider: str
    style: int
    injected: str


def _money(rng, lo, hi):
    return Decimal(rng.randint(lo * 100, hi * 100)) / 100


def make_case(rng: random.Random, injected=None) -> Case:
    n = rng.randint(2, 6)
    lines, descs = [], []
    for i in range(n):
        lines.append(Line(f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}",
                          f"SYN-{rng.randint(1000, 9999)}", _money(rng, 20, 900),
                          f"row{i}"))
        descs.append(rng.choice(DESCRIPTIONS))
    if injected == "duplicate_line":
        lines.append(lines[0])
        descs.append(descs[0])
    total = sum((l.billed for l in lines), Decimal("0"))
    owed = (total * Decimal(rng.choice(["0.1", "0.2", "0.3"]))).quantize(Decimal("0.01"))
    stated, responsibility = total, owed
    if injected == "sum_mismatch":
        stated = total + _money(rng, 5, 80)
    if injected == "eob_mismatch":
        responsibility = max(Decimal("0"), owed - _money(rng, 5, 60))
    bill = Bill(lines, stated, owed)
    return Case(bill, Eob([], responsibility), descs,
                f"Sample Clinic {rng.choice('ABCDEFG')}", rng.randint(0, 2),
                injected or "none")


def expected_flags(case: Case):
    return sorted(f.kind for f in run_checks(case.bill, case.eob))


def _font(size):
    for name in FONT_FILES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _scan_effect(img, rng):
    angle = rng.uniform(-1.2, 1.2)
    img = img.rotate(angle, expand=True, fillcolor="white")
    return img.filter(ImageFilter.GaussianBlur(rng.uniform(0.2, 0.7)))


def render_bill(case: Case, rng: random.Random) -> Image.Image:
    img = Image.new("RGB", (900, 280 + 44 * len(case.bill.lines) + 140), "white")
    d, f, fb = ImageDraw.Draw(img), _font(22), _font(26)
    d.text((40, 30), case.provider, font=fb, fill="black")
    d.text((40, 70), "STATEMENT  -  SYNTHETIC SAMPLE, NOT A REAL BILL", font=f, fill="#555")
    y = 130
    cols = {0: (40, 200, 360, 760), 1: (40, 170, 330, 700), 2: (500, 40, 160, 760)}[case.style]
    headers = ("Date", "Code", "Description", "Amount")
    if case.style == 2:
        headers = ("Amount", "Date", "Code", "Description")
    for h, x in zip(headers, (cols[0], cols[1], cols[2], cols[3])):
        d.text((x, y), h, font=fb, fill="black")
    d.line((40, y + 36, 860, y + 36), fill="black")
    y += 52
    for line, desc in zip(case.bill.lines, case.descriptions):
        amt = f"${line.billed:,.2f}"
        vals = (line.date, line.code, desc, amt)
        if case.style == 2:
            vals = (amt, line.date, line.code, desc)
        for v, x in zip(vals, (cols[0], cols[1], cols[2], cols[3])):
            d.text((x, y), v, font=f, fill="black")
        y += 44
    y += 20
    d.line((40, y, 860, y), fill="black")
    d.text((40, y + 20), f"Total charges: ${case.bill.stated_total:,.2f}", font=fb, fill="black")
    d.text((40, y + 62), f"Amount you owe: ${case.bill.patient_owes:,.2f}", font=fb, fill="black")
    return _scan_effect(img, rng)


def render_eob(case: Case, rng: random.Random) -> Image.Image:
    img = Image.new("RGB", (900, 420), "white")
    d, f, fb = ImageDraw.Draw(img), _font(22), _font(26)
    d.text((40, 30), "EXPLANATION OF BENEFITS", font=fb, fill="black")
    d.text((40, 70), "This is not a bill. SYNTHETIC SAMPLE.", font=f, fill="#555")
    total = sum((l.billed for l in case.bill.lines), Decimal("0"))
    d.text((40, 140), f"Amount billed by provider: ${total:,.2f}", font=f, fill="black")
    plan = total - case.eob.patient_responsibility
    d.text((40, 190), f"Plan paid: ${plan:,.2f}", font=f, fill="black")
    d.text((40, 260), f"Your responsibility: ${case.eob.patient_responsibility:,.2f}",
           font=fb, fill="black")
    return _scan_effect(img, rng)


def truth_dict(case: Case) -> dict:
    return {
        "injected": case.injected,
        "expected_flags": expected_flags(case),
        "bill": {"lines": [{"date": l.date, "code": l.code, "amount": str(l.billed)}
                           for l in case.bill.lines],
                 "stated_total": str(case.bill.stated_total),
                 "patient_owes": str(case.bill.patient_owes)},
        "eob": {"patient_responsibility": str(case.eob.patient_responsibility)},
    }


def generate(out_dir: Path, count=12, seed=1):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    for i in range(count):
        case = make_case(rng, ERRORS[i % len(ERRORS)])
        stem = out_dir / f"case_{i:03d}"
        render_bill(case, rng).save(f"{stem}_bill.png")
        render_eob(case, rng).save(f"{stem}_eob.png")
        Path(f"{stem}_truth.json").write_text(json.dumps(truth_dict(case), indent=2))
    return count


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/generated")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    s = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    print(f"wrote {generate(target, n, s)} cases to {target}")
