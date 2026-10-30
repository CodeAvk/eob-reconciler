"""Synthetic bill / EOB generator with known ground truth.

Everything is fictional: provider names, codes (opaque SYN-xxxx strings, not
real CPT codes) and amounts. Each case can inject one known error so that
extraction and checks can be scored against exact expectations.

CLI: python -m app.synthetic OUT_DIR [COUNT] [SEED] [hard]
"""
import io
import json
import random
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.core.checks import Bill, Eob, Line, run_checks

ERRORS = (None, "sum_mismatch", "duplicate_line", "eob_mismatch")
LONG_DESCRIPTIONS = ("Follow-up evaluation and management, established patient",
                     "Comprehensive metabolic panel with fasting collection",
                     "Outpatient imaging study, contrast, with interpretation",
                     "Physical therapy session, therapeutic exercise")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
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
    hard: bool = False
    extra: list = field(default_factory=list)  # distractor rows: (label, date, amount)


def _money(rng, lo, hi):
    return Decimal(rng.randint(lo * 100, hi * 100)) / 100


def _print_date(iso: str, style: int) -> str:
    y, m, d = iso.split("-")
    if style == 1:
        return f"{m}/{d}/{y}"
    if style == 2:
        return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"
    return iso


def _hard_code(rng):
    kind = rng.randint(0, 2)
    if kind == 0:
        return f"SYN-{rng.randint(1000, 9999)}"
    if kind == 1:
        return str(rng.randint(10000, 99999))
    return f"{rng.choice('ABJG')}{rng.randint(1000, 9999)}"


def _hard_extra(rng, date_style):
    rows = []
    for _ in range(rng.randint(1, 2)):
        iso = f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}"
        label = rng.choice(("Payment received", "Insurance adjustment", "Courtesy discount"))
        rows.append((label, _print_date(iso, date_style), f"-${_money(rng, 10, 300):,.2f}"))
    return rows


def make_case(rng: random.Random, injected=None, hard=False) -> Case:
    n = rng.randint(2, 6)
    lines, descs = [], []
    date_style = rng.randint(0, 2) if hard else 0
    for i in range(n):
        iso = f"2026-{rng.randint(1, 9):02d}-{rng.randint(1, 28):02d}"
        code = _hard_code(rng) if hard else f"SYN-{rng.randint(1000, 9999)}"
        amount = _money(rng, 20, 4000) if hard else _money(rng, 20, 900)
        lines.append(Line(_print_date(iso, date_style), code, amount, f"row{i}"))
        descs.append(rng.choice(LONG_DESCRIPTIONS if hard else DESCRIPTIONS))
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
                injected or "none", hard, _hard_extra(rng, date_style) if hard else [])


def expected_flags(case: Case):
    return sorted(f.kind for f in run_checks(case.bill, case.eob))


def _font(size):
    for name in FONT_FILES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _hard_scan(img, rng):
    """Heavier damage: tint, noise, rotation, blur and JPEG artifacts."""
    paper = (rng.randint(238, 252), rng.randint(236, 250), rng.randint(220, 245))
    tint = Image.new("RGB", img.size, paper)
    ink = img.convert("L").point(lambda v: 255 if v < 200 else 0)
    img = Image.composite(img, tint, ink)
    noise = Image.effect_noise(img.size, rng.uniform(14, 26)).convert("RGB")
    img = Image.blend(img, noise, 0.12)
    img = img.rotate(rng.uniform(-2.5, 2.5), expand=True, fillcolor=(245, 243, 235))
    img = img.filter(ImageFilter.GaussianBlur(rng.uniform(0.6, 1.1)))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=rng.randint(30, 50))
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB")


def _scan_effect(img, rng, hard=False):
    if hard:
        return _hard_scan(img, rng)
    angle = rng.uniform(-1.2, 1.2)
    img = img.rotate(angle, expand=True, fillcolor="white")
    return img.filter(ImageFilter.GaussianBlur(rng.uniform(0.2, 0.7)))


def _wrap(text: str, width: int = 24):
    words, rows, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            rows.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    return rows + [cur]


def render_bill(case: Case, rng: random.Random) -> Image.Image:
    wrapped = [_wrap(desc) if case.hard else [desc] for desc in case.descriptions]
    body_rows = sum(max(len(w), 1) for w in wrapped) + len(case.extra)
    img = Image.new("RGB", (900, 330 + 44 * body_rows + 140), "white")
    d, f, fb = ImageDraw.Draw(img), _font(22), _font(26)
    d.text((40, 30), case.provider, font=fb, fill="black")
    d.text((40, 70), "STATEMENT  -  SYNTHETIC SAMPLE, NOT A REAL BILL", font=f, fill="#555")
    y = 130
    cols = {0: (40, 200, 360, 760), 1: (40, 170, 330, 700), 2: (500, 40, 160, 760)}[case.style]
    headers = ("Date", "Code", "Description", "Amount")
    if case.style == 2:
        headers = ("Amount", "Date", "Code", "Description")
    for h, x in zip(headers, cols):
        d.text((x, y), h, font=fb, fill="black")
    d.line((40, y + 36, 860, y + 36), fill="black")
    y += 52
    for line, desc_rows in zip(case.bill.lines, wrapped):
        amt = f"${line.billed:,.2f}"
        vals = (line.date, line.code, desc_rows[0], amt)
        if case.style == 2:
            vals = (amt, line.date, line.code, desc_rows[0])
        for v, x in zip(vals, cols):
            d.text((x, y), v, font=f, fill="black")
        desc_x = cols[3] if case.style == 2 else cols[2]
        for extra_row in desc_rows[1:]:
            y += 34
            d.text((desc_x, y), extra_row, font=f, fill="black")
        y += 44
    for label, date, amount in case.extra:  # payments/adjustments: no code, not charges
        vals = (date, "", label, amount)
        if case.style == 2:
            vals = (amount, date, "", label)
        for v, x in zip(vals, cols):
            d.text((x, y), v, font=f, fill="#222")
        y += 44
    y += 20
    d.line((40, y, 860, y), fill="black")
    d.text((40, y + 20), f"Total charges: ${case.bill.stated_total:,.2f}", font=fb, fill="black")
    d.text((40, y + 62), f"Amount you owe: ${case.bill.patient_owes:,.2f}", font=fb, fill="black")
    return _scan_effect(img, rng, case.hard)


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
    return _scan_effect(img, rng, case.hard)


def truth_dict(case: Case) -> dict:
    return {
        "injected": case.injected,
        "hard": case.hard,
        "expected_flags": expected_flags(case),
        "bill": {"lines": [{"date": l.date, "code": l.code, "amount": str(l.billed)}
                           for l in case.bill.lines],
                 "stated_total": str(case.bill.stated_total),
                 "patient_owes": str(case.bill.patient_owes)},
        "eob": {"patient_responsibility": str(case.eob.patient_responsibility)},
    }


def generate(out_dir: Path, count=12, seed=1, hard=False):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)
    for i in range(count):
        case = make_case(rng, ERRORS[i % len(ERRORS)], hard)
        stem = out_dir / f"case_{i:03d}"
        render_bill(case, rng).save(f"{stem}_bill.png")
        render_eob(case, rng).save(f"{stem}_eob.png")
        Path(f"{stem}_truth.json").write_text(json.dumps(truth_dict(case), indent=2))
    return count


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/generated")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    s = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    is_hard = len(sys.argv) > 4 and sys.argv[4] == "hard"
    print(f"wrote {generate(target, n, s, is_hard)} cases to {target}")
