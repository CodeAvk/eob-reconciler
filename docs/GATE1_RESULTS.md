# Gate 1 results: does AI beat the simple solution?

Last updated: 2026-11-01. Task: extract bill line items, totals and the EOB patient amount, then run the deterministic checks. All documents are synthetic (`backend/app/synthetic.py`). Reproduce with the commands at the bottom.

## Verdict: line-extraction criterion NOT met; end-to-end accuracy clearly better

The plan required AI to reach line F1 >= 0.90 **and** beat the baseline by >= 10 points.

- **Line F1:** Gemini 0.970 vs 0.914 for a deskewed OCR + regex baseline, a margin of **+5.6 points**. Below the +10 the plan asked for, so the strict criterion is not met.
- **End-to-end flags:** Gemini gets the flags exactly right in 100% of cases vs 76.7% for the stronger baseline (+23 points), finds 22/22 injected errors vs 21/22, and raises **0 false alarms on 8 clean bills vs 4 of 8**. False alarms are the costly failure in this product, and a missed line makes a clean bill look wrong.

So AI adds a real but moderate advantage. It is mostly robustness: it handles varied dates, codes, tilt and noise without per-format rules. A more heavily engineered baseline could narrow the gap.

The owner chose to continue as a portfolio project (2026-10-31) and waived user interviews. Demand is **not validated**.

## Easy set (uniform, clean layouts)

| Extractor | Cases | Line F1 | Flags exact | Injected found | False alarms (clean) |
|---|---|---|---|---|---|
| OCR + regex | 32 | 1.000 | 1.00 | 24/24 | 0/8 |
| Gemini 2.5 Flash | 8 | 1.000 | 1.00 | 6/6 | 0/2 |

Clean, uniform documents are fully solved by free OCR + regex. No AI needed here.

## Hard set (seed 21): the same 30 cases for all three extractors

Hard mode adds three date formats, three code formats, thousands separators, wrapped descriptions, payment and adjustment rows, page tilt, blur, noise and JPEG damage. Gemini completed 30 of 32 cases; two failed (one transient HTTP 503, one daily-quota 429). All three extractors are scored on the same 30.

| Extractor | Line precision | Line recall | Line F1 | Flags exact | Injected found | False alarms (clean) |
|---|---|---|---|---|---|---|
| OCR + regex (plain) | 1.000 | 0.535 | 0.697 | 0.633 | 20/22 | 6/8 |
| OCR + regex + deskew | 1.000 | 0.842 | 0.914 | 0.767 | 21/22 | 4/8 |
| Gemini 2.5 Flash | 0.970 | 0.970 | 0.970 | 1.000 | 22/22 | 0/8 |

Amounts and totals: Gemini got the stated total, amount owed and EOB amount right in every one of the 30 cases. No amount was invented by any extractor.

### What each approach gets wrong

- **Plain baseline:** page tilt pushes amounts out of line with their dates, so lines are dropped, totals look wrong, and clean bills get false "sum mismatch" flags.
- **Deskew baseline:** it still misses lines, mostly those with long-format dates (such as "Mar 23, 2026") and varied code shapes. These look fixable with more rules.
- **Gemini:** 3 of 101 lines had altered codes: a dropped letter prefix twice (`A9326` became `9326`) and a leading zero added once (`80603` became `080603`). Amounts were correct, but silently changed values are a real risk, so the UI tells users to verify against the original.

## End-to-end check on the real stack (2026-11-01)

One synthetic pair with a known duplicate charge went through upload, MinIO, MongoDB, Redis, Celery, Gemini and the checks. The duplicate was found in about 9 seconds with no false flags, and the case, files and queue entries were confirmed in MongoDB, MinIO and Redis. This also surfaced a bug: the cited evidence was the word "bill" instead of the printed row. It is fixed (schema description plus a guard that labels reconstructed text), and a re-run cited the real rows.

## Quota and speed

- Free tier for `gemini-2.5-flash`: **20 requests per day**, and retries on 503 count against it. One request per case, so about 20 cases per day at best.
- Gemini: median about 12 s per case. Baseline: about 18 s per case on this CPU, almost all OCR.

## Caveats

- All data is synthetic and written by me. Real bills vary more.
- I built the hard set after seeing the baseline score 100% on the easy set, which risks favouring AI. The deskew baseline was also added after seeing the plain baseline fail. Both were one-pass changes made in the open, but treat the numbers as a stress test, not an estimate of real-world accuracy.
- Small samples: 30 cases, 8 of them clean. The first 18 Gemini results were produced before the evidence-citation fix. That change touched only the `source` text, not the extracted values.
- Two hard cases (case_027, case_031) were not scored for Gemini because of API errors.
- No real documents were used. Free-tier terms say not to send personal or health data.
- User demand is not validated (Gate 2 waived).

## Next steps

1. Run Gemini on case_027 and case_031 when the quota resets.
2. Optionally improve the baseline's long-date handling and re-measure the margin.
3. Report these numbers, including the sub-10-point line-F1 margin, in the README.

## Reproduce

```
cd backend
python -m app.synthetic ../data/generated/gate1 32 7
python -m app.synthetic ../data/generated/gate1_hard 32 21 hard
python -m app.evaluate ../data/generated/gate1_hard --extractor baseline
python -m app.evaluate ../data/generated/gate1_hard --extractor baseline_deskew
python -m app.evaluate ../data/generated/gate1_hard --extractor gemini --limit 32
```

Raw per-case reports are written to `data/eval/` (git-ignored).
