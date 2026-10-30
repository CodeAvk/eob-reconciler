# PLAN.md

Status as of 2026-10-30: research done; Gate 0 partial; Gate 1 pending (baseline built and scored, Gemini hard-set run blocked by the free 20 requests/day quota). Skeleton app (FastAPI, Celery, MongoDB, MinIO, Next.js) exists but is not validated end to end, and the owner chose to build it ahead of the gates. See `docs/GATE1_RESULTS.md`.

## Phases
1. **Research** — done. See `PRODUCT_RESEARCH.md`. 5 ideas assessed: 2 rejected, 2 on hold, 1 conditional candidate (Bill↔EOB Reconciler).
2. **Gate 0: free API access** — key works; measured limit is 20 requests/day; privacy approach for real data still undecided.
3. **Gate 1: AI vs non-AI baseline** on synthetic data. Reject if AI doesn't win.
4. **Gate 2: user validation** — real interviews and concierge test, honestly logged.
5. **Gate 3: narrow MVP** — only if Gates 0–2 pass.
6. **Publish** — repo `CodeAvk/eob-reconciler` (private) exists. Each push follows the checklist in `CLAUDE.md` plus tests and a security scan.

## Next actions
- [ ] Run Gemini on the 32 hard cases (1 request per case; the free limit allows about 20 per day).
- [ ] If AI clears the Gate 1 bar: build a stronger baseline (deskew, table detection) and re-test.
- [x] Synthetic generator, baseline and evaluation harness (done 2026-10-30).
- [ ] Draft the interview script (no outreach until reviewed).

## Decisions (2026-10-29)
- AI backend: free-tier APIs (Gemini first); hard-coded logic where no free API fits. No local models.
- Git identity set locally: CodeAvk / avksmlavk@gmail.com. Pushes use a fine-grained token from `.env`; `gh` is not installed.

## Open questions for the owner
- Free tiers say not to send personal/health data. For the medical-bill idea, pick: redact-then-send, user's own key, or switch to a non-sensitive domain?
- Is the US medical-bill domain still acceptable?

## Work not done
No benchmarks, no interviews, no competitor pricing for Goodbill/MBAA, no primary-source check of the 2024 JAMA claim.
