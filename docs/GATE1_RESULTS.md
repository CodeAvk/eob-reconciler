# Gate 1 results: does AI beat the simple solution?

Last updated: 2026-10-31. Task: extract bill line items, totals and the EOB patient amount, then run the deterministic checks. All documents are synthetic (`backend/app/synthetic.py`). Reproduce with the commands at the bottom.

## Verdict: NOT PASSED under the plan's strict rule, with a real but modest AI advantage

The plan required AI to reach line F1 >= 0.90 **and** beat the baseline by >= 10 points. Gemini reaches 0.947, but a stronger non-AI baseline reaches 0.935 on the same cases, a margin of 1.2 points. By the plan's rule that means "AI adds no meaningful value on line extraction".

Where AI does help is end-to-end accuracy: exactly-right flags and fewer false alarms on clean bills. That evidence is thin (18 cases, only 5 clean), so it is a signal, not a proof.

The owner chose to continue as a portfolio project (2026-10-31). The honest story for the README is: "I measured AI against a well-engineered rules baseline and found a small edge, mostly in robustness."

## Easy set (uniform, clean layouts)

| Extractor | Cases | Line F1 | Flags exact | Injected found | False alarms (clean) |
|---|---|---|---|---|---|
| OCR + regex | 32 | 1.000 | 1.00 | 24/24 | 0/8 |
| Gemini 2.5 Flash | 8 | 1.000 | 1.00 | 6/6 | 0/2 |

Clean, uniform documents are fully solved by free OCR + regex. No AI needed here.

## Hard set (seed 21): same 18 cases for all three extractors

Hard mode adds three date formats, three code formats, thousands separators, wrapped descriptions, payment and adjustment rows, page tilt, blur, noise and JPEG damage.

| Extractor | Line F1 | Line recall | Flags exact | Injected found | False alarms (clean) |
|---|---|---|---|---|---|
| OCR + regex (plain) | 0.690 | 0.526 | 0.611 | 12/13 | 4/5 |
| OCR + regex + deskew | 0.935 | 0.877 | 0.833 | 13/13 | 2/5 |
| Gemini 2.5 Flash | 0.947 | 0.947 | 1.000 | 13/13 | 0/5 |

Deskew baseline on all 32 hard cases: line F1 0.907, recall 0.830, flags exact 0.750, 23/24 injected found, 4/8 false alarms. Gemini has not been run on the remaining 14 hard cases yet (daily quota).

### What each approach gets wrong

- **Plain baseline:** page tilt pushes amounts out of line with their dates, so lines are dropped, totals look wrong, and clean bills get false "sum mismatch" flags.
- **Deskew baseline:** the 18 lines it still misses were mostly with long-format dates (such as "Mar 23, 2026") and varied code shapes. These look fixable with more rules. **More baseline effort could close the remaining gap**, so the AI advantage may be smaller than shown.
- **Gemini:** 3 of 57 lines had altered codes: it dropped a letter prefix twice (`A9326` became `9326`) and added a leading zero once (`80603` became `080603`). Amounts were correct and no amounts were invented, but silently changed values are a real risk and the UI tells users to verify against the original.

## Quota and speed

- Free tier for `gemini-2.5-flash`: **20 requests per day** (from the API's 429 message, measured 2026-10-30). One request per case, so about 20 cases per day.
- Gemini: median 11.7 s per case (max 27 s). Baseline: about 18 s per case on this CPU, almost all OCR.

## Caveats

- All data is synthetic and written by me. Real bills vary more.
- I built the hard set after seeing the baseline score 100% on the easy set, which risks favouring AI. The deskew baseline was also added after seeing the plain baseline fail. Both were one-pass changes made in the open, but treat the numbers as a stress test, not an estimate of real-world accuracy.
- Sample sizes are small: 18 Gemini cases, 5 clean.
- No real documents were used. Free-tier terms say not to send personal or health data.
- User demand is not validated (Gate 2 waived).

## Next steps

1. Run Gemini on the remaining 14 hard cases (14 requests, next quota window).
2. Decide whether to improve the baseline further (long-date handling) and re-measure, to see how large the AI margin really is.
3. Report the final numbers in the README, including the weak line-F1 margin.

## Reproduce

```
cd backend
python -m app.synthetic ../data/generated/gate1 32 7
python -m app.synthetic ../data/generated/gate1_hard 32 21 hard
python -m app.evaluate ../data/generated/gate1_hard --extractor baseline
python -m app.evaluate ../data/generated/gate1_hard --extractor baseline_deskew
python -m app.evaluate ../data/generated/gate1_hard --extractor gemini --limit 18
```

Raw per-case reports are written to `data/eval/` (git-ignored).
