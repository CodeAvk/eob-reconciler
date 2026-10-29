# VALIDATION_PLAN.md

Rule: **No product implementation until Gates 0–2 pass.** Results must be recorded as they actually happened. Never invent interviews, quotes, or numbers. If a gate fails, record it and reject or pivot the idea.

## Gate 0 — Free API access and terms (≈1 day, free)
- [ ] Create a free Gemini API key (personal account); store in git-ignored `.env`.
- [ ] Record live free-tier limits from AI Studio (RPM/RPD/TPM) and re-read the data terms; note date.
- [ ] Confirm a vision/PDF extraction call works on a synthetic page within quota; record latency and quota used per document.
- [ ] Decide the privacy approach for real data (redact-then-send / user's own key / change domain). Test redaction recall if chosen.
- [ ] Pass: ≥ 30 documents processable per day within free limits, and a privacy approach is chosen. Fail → hard-code or change idea.
- [ ] Local models are no longer part of the plan unless the owner reverses this.

## Gate 1 — Does AI beat the simple solution? (≈1 week)
- [ ] Build a **synthetic** test set: ≥ 30 bill + EOB pairs with varied layouts/scan quality, generated with known ground truth. No real PHI.
- [ ] Baseline A (non-AI): OCR + regex/templates (free libs). Baseline B: free-API extraction (Gemini vision/JSON schema output).
- [ ] Metrics: field-level F1, fabricated-value rate, seconds per doc.
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
