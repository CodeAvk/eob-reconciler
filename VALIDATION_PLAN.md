# VALIDATION_PLAN.md

Rule: **No product implementation until Gates 0–2 pass.** Results must be recorded as they actually happened. Never invent interviews, quotes, or numbers. If a gate fails, record it and reject or pivot the idea.

## Gate 0 — Free API access and terms (≈1 day, free)
- [x] Create a free Gemini API key (personal account); store in git-ignored `.env`. (done 2026-10-29)
- [x] Record live free-tier limits and re-read the data terms. Measured 2026-10-30: gemini-2.5-flash allows 20 requests per day on the free tier (from the API's 429 message). Data terms unchanged: not for sensitive data.
- [x] Confirm a vision extraction call works on synthetic pages. Latency about 14 s per case plus pauses; now 1 request per case.
- [ ] Decide the privacy approach for real data (redact-then-send / user's own key / change domain). Test redaction recall if chosen.
- [ ] Pass: ≥ 30 documents processable per day within free limits, and a privacy approach is chosen. **Status 2026-10-30: NOT MET.** The free limit allows about 20 cases per day (1 request each), and the privacy approach for real data is still undecided. Fine for evaluation, a hard ceiling for real users.
- [ ] Local models are no longer part of the plan unless the owner reverses this.

## Gate 1 — Does AI beat the simple solution? (≈1 week)
- [x] Build a **synthetic** test set: ≥ 30 bill + EOB pairs with varied layouts/scan quality, generated with known ground truth. No real PHI. (32 easy + 32 hard, 2026-10-30)
- [x] Baseline A (non-AI): OCR + regex (RapidOCR). Done, scored on all 64 cases.
- [ ] Baseline B: free-API extraction (Gemini). Easy set: 8 of 32 cases. Hard set: 0 of 32, blocked by the 20 requests/day quota. See `docs/GATE1_RESULTS.md`.
- [x] Metrics: line precision/recall/F1, fabricated lines, field accuracy, flag accuracy, false alarms, seconds per case.
- [ ] Pass: B ≥ 0.90 F1, ≥ 10 points over A, 0 fabricated line items. **Fail → reject the idea** (AI adds no meaningful value). Fall back to idea 3 bake-off, or stop.

## Gate 2 — Is the problem real and does the AI part matter to users? (≈2–3 weeks)
Honest, low-cost methods only:
- [ ] Draft a short screener and interview script (problem, not solution). Ask about the last disputed/confusing medical bill, what they did, time/money spent.
- [ ] Recruit ≥ 8 people with a recent medical-bill experience from my own network and relevant public communities (follow each community's rules; no spam). Record counts of those contacted vs. replied.
- [ ] Log every interview in `validation/interviews/` with date, anonymized ID, notes. Only real ones.
- [ ] Concierge test: for ≥ 5 consenting participants, run the tool on their own redacted documents (or a walk-through using synthetic docs) and ask whether the cited findings would change their action. Participants never upload data without consent; delete after.
- [ ] Pass: ≥ 5 of 8 report a real recent problem; ≥ 3 would use it next time, with a concrete trigger. Willingness-to-pay is noted but not required. Fail → reject or reposition.

## Gate 3 — Narrow MVP build (only after Gates 0–2)
- [ ] Implement exactly the MVP scope in `PRODUCT_RESEARCH.md`.
- [ ] Tests: unit tests for deterministic checks; evaluation harness reruns Gate 1 numbers in CI-like script.
- [ ] Security: secret scan, dependency audit, confirm no network calls at inference, no real data in repo.
- [ ] Success criteria from `PRODUCT_RESEARCH.md` must be re-measured and reported, whether they pass or not.

## Kill criteria
Stop or pivot if any: Gate 1 fails; fewer than 3 of 8 interviewees have a real problem; local latency > 3 min/doc with no workaround; a free tool already does the same with local-only processing and evidence-cited flags (re-check competitors before Gate 3).

## Publishing gate (separate from product gates)
Before any GitHub repo creation or push: complete the checklist in `CLAUDE.md` (git author, remote, `gh auth status` = `CodeAvk`), run tests and security checks. Commit only real work. No filler commits.

## Log
| Date | Gate | Result | Notes |
|------|------|--------|-------|
| 2026-10-28 | research | done | Desk research only. No validation performed yet. |
| 2026-10-29 | Gate 0 | partial | Key works. Privacy approach for real data undecided. |
| 2026-10-30 | Gate 1 | pending | Baseline scores 1.00 on easy set but 0.54 line recall on hard set (32 cases). Gemini perfect on 8 easy cases, not yet measured on hard set (free quota 20/day). See docs/GATE1_RESULTS.md. |
