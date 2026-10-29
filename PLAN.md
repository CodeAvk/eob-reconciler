# PLAN.md

Status as of 2026-10-28: research complete (desk only), validation not started, no product code.

## Phases
1. **Research** — done. See `PRODUCT_RESEARCH.md`. 5 ideas assessed: 2 rejected, 2 on hold, 1 conditional candidate (Bill↔EOB Reconciler).
2. **Gate 0: environment** — install local runtime, benchmark CPU inference.
3. **Gate 1: AI vs non-AI baseline** on synthetic data. Reject if AI doesn't win.
4. **Gate 2: user validation** — real interviews and concierge test, honestly logged.
5. **Gate 3: narrow MVP** — only if Gates 0–2 pass.
6. **Publish** — only after the personal-account checklist in `CLAUDE.md`, tests and security checks. Not authorized yet.

## Next actions
- [ ] Set a repo-local git identity for the personal account (global identity is employer's); make the first real commit when ready.
- [ ] Gate 0 benchmarks.
- [ ] Build synthetic bill/EOB generator and the baseline.
- [ ] Draft the interview script (no outreach until reviewed).

## Decisions (2026-10-29)
- AI backend: free-tier APIs (Gemini first); hard-coded logic where no free API fits. No local models.
- Git identity set locally: CodeAvk / avksmlavk@gmail.com. No remote, no commits yet. `gh` not installed.

## Open questions for the owner
- Free tiers say not to send personal/health data. For the medical-bill idea, pick: redact-then-send, user's own key, or switch to a non-sensitive domain?
- Is the US medical-bill domain still acceptable?

## Work not done
No benchmarks, no interviews, no competitor pricing for Goodbill/MBAA, no primary-source check of the 2024 JAMA claim.
