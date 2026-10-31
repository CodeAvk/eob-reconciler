# PLAN.md

Status as of 2026-10-31: research done; Gate 0 partial; Gate 1 not passed under the strict rule (Gemini F1 0.947 vs 0.935 for a deskewed baseline; AI edge is in flag accuracy and false alarms); Gate 2 waived; continuing as a portfolio project. Skeleton app (FastAPI, Celery, MongoDB, MinIO, Next.js) exists but is not validated end to end, and the owner chose to build it ahead of the gates. See `docs/GATE1_RESULTS.md`.

## Phases
1. **Research** — done. See `PRODUCT_RESEARCH.md`. 5 ideas assessed: 2 rejected, 2 on hold, 1 conditional candidate (Bill↔EOB Reconciler).
2. **Gate 0: free API access** — key works; measured limit is 20 requests/day; privacy approach for real data still undecided.
3. **Gate 1: AI vs non-AI baseline** on synthetic data. Reject if AI doesn't win.
4. **Gate 2: user validation** — WAIVED by the owner (2026-10-31). Portfolio project; demand is not validated and is never claimed.
5. **Gate 3: narrow MVP** — after Gate 0 and Gate 1 (with the owner's privacy decision).
6. **Publish** — repo `CodeAvk/eob-reconciler` (private) exists. Each push follows the checklist in `CLAUDE.md` plus tests and a security scan.

## Next actions
- [ ] Run Gemini on the remaining 14 hard cases (14 requests, next quota window).
- [ ] Optionally fix the baseline's long-date handling and re-measure the AI margin.
- [x] Synthetic generator, baseline and evaluation harness (done 2026-10-30).
- [x] Interview script drafted (`docs/INTERVIEW_SCRIPT.md`), kept as an optional path only.
- [ ] End-to-end run of the full app with Docker, then fix what breaks.
- [ ] Privacy handling (redaction before any API call) and tests.
- [ ] README with an honest scope statement, run guide and the Gate 1 numbers.

## Decisions (2026-10-29)
- AI backend: free-tier APIs (Gemini first); hard-coded logic where no free API fits. No local models.
- Git identity set locally: CodeAvk / avksmlavk@gmail.com. Pushes use a fine-grained token from `.env`; `gh` is not installed.

## Open questions for the owner
- Free tiers say not to send personal/health data. For the medical-bill idea, pick: redact-then-send, user's own key, or switch to a non-sensitive domain?
- Is the US medical-bill domain still acceptable?

## Work not done
No benchmarks, no interviews, no competitor pricing for Goodbill/MBAA, no primary-source check of the 2024 JAMA claim.
