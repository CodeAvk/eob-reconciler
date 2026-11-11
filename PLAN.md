# PLAN.md

Status as of 2026-11-01: research done; Gate 0 partial; Gate 1: line-F1 margin +5.6 pts (rule needs +10) but flag accuracy 100% vs 77% and 0/8 vs 4/8 false alarms; full app verified end to end on Docker; Gate 2 waived; continuing as a portfolio project. Skeleton app (FastAPI, Celery, MongoDB, MinIO, Next.js) exists but is not validated end to end, and the owner chose to build it ahead of the gates. See `docs/GATE1_RESULTS.md`.

## Phases
1. **Research** — done. See `PRODUCT_RESEARCH.md`. 5 ideas assessed: 2 rejected, 2 on hold, 1 conditional candidate (Bill↔EOB Reconciler).
2. **Gate 0: free API access** — key works; measured limit is 20 requests/day; privacy approach for real data still undecided.
3. **Gate 1: AI vs non-AI baseline** on synthetic data. Reject if AI doesn't win.
4. **Gate 2: user validation** — WAIVED by the owner (2026-10-31). Portfolio project; demand is not validated and is never claimed.
5. **Gate 3: narrow MVP** — after Gate 0 and Gate 1 (with the owner's privacy decision).
6. **Publish** — repo `CodeAvk/eob-reconciler` (public) exists. Each push follows the checklist in `CLAUDE.md` plus tests and a security scan. Since 2026-11-11, GitHub Actions CI runs the backend tests, frontend build, dependency audits and a gitleaks scan on every push to `main` and every pull request.

## Next actions
- [ ] Run Gemini on the 2 unscored hard cases (case_027, case_031) when quota resets.
- [ ] Optionally fix the baseline's long-date handling and re-measure the AI margin.
- [x] Synthetic generator, baseline and evaluation harness (done 2026-10-30).
- [x] Interview script drafted (`docs/INTERVIEW_SCRIPT.md`), kept as an optional path only.
- [x] End-to-end run of the full app with Docker (2026-11-01): fixed Redis port clash, CORS config and evidence citations.
- [ ] Privacy handling (redaction before any API call) and tests.
- [x] README with an honest scope statement, run guide and the Gate 1 numbers (2026-11-01).

## Decisions (2026-10-29)
- AI backend: free-tier APIs (Gemini first); hard-coded logic where no free API fits. No local models.
- Git identity set locally: CodeAvk / avksmlavk@gmail.com. Pushes use a fine-grained token from `.env`; `gh` is not installed.
  - Update 2026-11-11: `gh` is now installed and signed in as CodeAvk; pushes use it as the credential helper per command, not the `.env` token.

## Open questions for the owner
- Free tiers say not to send personal/health data. For the medical-bill idea, pick: redact-then-send, user's own key, or switch to a non-sensitive domain?
- Is the US medical-bill domain still acceptable?

## Work not done
No benchmarks, no interviews, no competitor pricing for Goodbill/MBAA, no primary-source check of the 2024 JAMA claim.
