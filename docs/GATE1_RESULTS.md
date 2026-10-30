# Gate 1 results: does AI beat the simple solution?

Date: 2026-10-30. Task: extract bill line items, totals and the EOB patient amount, then run the deterministic checks. All documents are synthetic (see `backend/app/synthetic.py`). Reproduce with the commands at the bottom.

## Verdict: PENDING (not passed, not failed)

The Gemini run on the hard set could not be completed today because the free-tier daily quota ran out (details below). The plan's rule is unchanged: AI must reach line F1 >= 0.90 **and** beat the baseline by >= 10 points on the hard set, otherwise the idea is rejected or reworked.

## Round 1: easy set (uniform, clean layouts)

| Extractor | Cases | Line F1 | Total / owes / EOB acc | Flags exact | Injected errors found | False alarms on clean cases |
|---|---|---|---|---|---|---|
| OCR + regex baseline | 32 | 1.000 | 1.00 / 1.00 / 1.00 | 1.00 | 24/24 | 0/8 |
| Gemini 2.5 Flash | 8 | 1.000 | 1.00 / 1.00 / 1.00 | 1.00 | 6/6 | 0/2 |

Finding: on clean, uniform documents a free OCR + regex pipeline is already perfect. This round says nothing in favour of AI. Gemini's sample (8) is below the plan's 30-case minimum.

## Round 2: hard set (seed 21, 32 cases)

Hard mode adds three date formats, three code formats, thousands separators, wrapped descriptions, payment and adjustment distractor rows, page tilt, blur, noise and JPEG damage.

| Extractor | Cases | Line precision | Line recall | Line F1 | Total acc | Flags exact | Injected found | False alarms on clean |
|---|---|---|---|---|---|---|---|---|
| OCR + regex baseline | 32 | 1.000 | 0.538 | 0.699 | 0.969 | 0.625 | 22/24 | 6/8 |
| Gemini 2.5 Flash | 0 | not measured | | | | | | |

Baseline on the first 12 hard cases (the subset Gemini will be scored on first): line recall 0.657, F1 0.793, flags exact 0.667, 8/9 injected found, 2/3 false alarms.

Why the baseline fails: tilted pages push amounts out of line with their dates, and wrapped descriptions split rows, so lines are dropped. Dropped lines make the stated total look wrong, which creates false "sum mismatch" alarms on clean bills. False alarms are the costly failure for this product.

## Why Gemini was not measured

The free tier for `gemini-2.5-flash` allows **20 requests per day** (error text: "generate_content_free_tier_requests, limit: 20, model: gemini-2.5-flash"). The easy-set run used 16, and 12 further hard-set calls returned HTTP 429. This also corrects my earlier local cap of 50, which was wrong; the cap is now 20.

Fix made: bill and EOB now go in one request, so a case costs 1 request. That gives about 20 cases per day, enough for evaluation but a hard limit on any real use of the free tier.

## Caveats that weaken these results

- All data is synthetic and was written by me. Real bills vary far more, and may be easier or harder.
- I built the hard set **after** seeing the baseline score 100% on the easy set. That risks designing a test that favours AI. Treat the hard-set numbers as a stress test, not a fair estimate of real-world performance.
- The baseline is a simple row-grouping implementation with one bounded tuning round. A layout-aware baseline (table detection, deskewing) would likely score higher, so the gap shown may overstate the benefit of AI.
- The free-tier terms say not to send personal or health data, so none of this has touched real documents.
- Speed: the baseline averages about 18 s per case on this CPU (almost all OCR). Gemini took about 20 s per case including deliberate pauses.

## Next steps

1. When quota resets: run Gemini on the first 12 hard cases (12 requests), then the remaining 20 over the next day.
2. If AI clears the bar: add a stronger baseline (deskew + table detection) and re-test before claiming a win.
3. If AI does not clear the bar: reject or rework the idea per the validation plan.

## Reproduce

```
cd backend
python -m app.synthetic ../data/generated/gate1 32 7          # easy set
python -m app.synthetic ../data/generated/gate1_hard 32 21 hard
python -m app.evaluate ../data/generated/gate1_hard --extractor baseline
python -m app.evaluate ../data/generated/gate1_hard --extractor gemini --limit 12
```

Raw per-case reports are written to `data/eval/` (git-ignored).
