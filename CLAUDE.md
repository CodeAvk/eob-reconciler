# CLAUDE.md — Workspace rules

Personal product-development workspace. Owner's personal GitHub account: `CodeAvk` (https://github.com/CodeAvk).

## Product requirements
- AI is mandatory in every product considered, and it must do real work: document extraction, classification, prediction, anomaly detection, evidence-based summarization, intelligent automation, or decision support.
- A generic chatbot, or a CRUD app with an AI chat box, does not qualify.
- Every idea must beat a simpler non-AI baseline. If AI adds no measurable value, reject the idea and record why in `PRODUCT_RESEARCH.md`.
- **AI backend decision (owner, 2026-10-29): use free-tier AI APIs (e.g. Gemini), not local/built-in models. If no free API fits a task, hard-code deterministic logic for it instead.** Never fake AI output with canned answers presented as AI.
- Verify each free tier's current limits and data terms on the provider's own page before building on it; free tiers change often. Keys go in env vars / `.env` (git-ignored), never in the repo. Do not assume paid usage; stay inside free quota.
- Free-tier terms may allow provider training on submitted data (Gemini: yes outside EEA/UK/CH, and it says not to submit sensitive/personal data). Send only synthetic or non-sensitive data to a free API. Report privacy honestly.
- Never fabricate interviews, customer feedback, demand, benchmarks or sources. Mark unverified claims as unverified.
- Do not implement a product until the gates in `VALIDATION_PLAN.md` are met.

## Dev hardware (measured 2026-10-28)
Intel i5-1334U, ~31.7 GB RAM, no NVIDIA GPU. No local LLMs are used (owner decision); only the non-AI OCR baseline runs on CPU, about 18 s per case.

## Git and GitHub safety (personal vs employer)
- The global git identity on this machine is a **work** identity. Never commit or push with it.
- Repo-local identity is set (2026-10-29): `user.name=CodeAvk`, `user.email=avksmlavk@gmail.com`. Verify it again before each push.
- `gh` CLI is not installed on this machine; install and run `gh auth status` before any publishing (expected account: CodeAvk).
- Before any push or repo creation: check `git config user.name`, `git config user.email`, `git remote -v`, and `gh auth status` (never print tokens). All must be `CodeAvk` / personal. If anything is ambiguous or employer-related, stop and report.
- Never push to company repos. Never copy company code, secrets, data or proprietary material here.
- Run tests and security checks (secret scan, dependency audit) before every push.
- No fake commits, filler code, or scheduled changes to inflate the contribution graph. Commit only real work.
- Current state: local commits only, no remote. GitHub repo creation and push are not done yet; the owner wants one commit per real feature, pushed once a personal repo exists.

## Data rules
- No real personal, health or financial data in the repo or in tests. Use synthetic documents only.
- Respect dataset and code licences (e.g. CC BY-NC-SA data is not usable in a product; AMA owns CPT code descriptions).

## Workflow and pacing (owner, 2026-10-29)
- Goal: one valuable, finished AI project, with a GitHub history that reads as steady, consistent, real work.
- One feature per commit, pushed only when that feature is finished, tested and verified. Do not push several features in one session just to catch up.
- Take time on each step; quality over speed. New projects are started one at a time, after the current one meets its gates.
- Never backdate commits, fake timestamps, or create filler commits to shape the contribution graph. History must match the real work.
- Push method: token in the git-ignored `.env` as `GITHUB_TOKEN`, passed per command via `http.extraheader`; never printed or stored. Token expires about 2026-11-28, so remind the owner before then.
