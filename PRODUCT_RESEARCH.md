# PRODUCT_RESEARCH.md

Research date: 2026-10-28. Method: web searches (standard mode) and one repo fetch. **No interviews or user feedback exist yet.** Most "demand" figures below come from vendors or advocacy groups and are labelled as such. Items marked **UNVERIFIED** were not confirmed against a primary source.

## Update 2026-10-29 — owner chose free AI APIs over local models
Owner instruction: use free AI APIs (e.g. Gemini); hard-code logic where no free API exists. This supersedes the local-first preference below. Findings:
- **Gemini free tier:** the rate-limit page lists no free-tier numbers (check AI Studio for live limits) ([docs](https://ai.google.dev/gemini-api/docs/rate-limits)). Reported 2026 cuts to free quotas are from secondary sources only.
- **Gemini terms (unpaid services):** Google uses submitted content and responses to improve its products, human reviewers may read them, and it says "Do not submit sensitive, confidential, or personal information." In EEA/UK/CH the paid-data terms apply (no training), but API clients serving users there may only use paid services ([terms](https://ai.google.dev/gemini-api/terms)).
- **Other free tiers (secondary sources, verify):** Groq ~30 RPM / 1K req/day on one model; OpenRouter `:free` models 20 RPM / 50 req/day; Mistral Experiment tier ~1B tokens/month, may require data-training consent ([OpenRouter comparison](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/), [KDnuggets](https://kdnuggets.com/5-free-llm-api-providers-you-can-use-in-2026)). Vision/document-input limits for these: not found.
- **Impact on idea 5 (medical bills):** real bills are health data, which free tiers say not to receive. Development and evaluation can use synthetic documents only. For real users the options are: (a) redact names/IDs locally by deterministic code before any API call and send only line-item text, (b) user supplies their own key and accepts the terms, or (c) switch domain to non-sensitive documents. Option (a) is cheapest but redaction reliability must itself be tested. **Owner decision needed.**
- **Impact on idea 1/3:** better free vision APIs raise extraction quality, but idea 1 stays crowded; idea 3 leases also contain personal data.
- The cost line "$0 operating" now means "within free quota", with rate limits that cap throughput.

## Constraints
- Hardware: i5-1334U, ~31.7 GB RAM, no NVIDIA GPU → CPU-only. A third-party report of ~9 tok/s for a 7B Q4 model on a 16 GB Intel laptop ([source](https://insiderllm.com/pdfs/cpu-only-llms-what-actually-works.pdf), mixed-hardware, unconfirmed). Real speed on this machine: **not measured**.
- Operating cost target: $0 (local inference, self-hosted).

## Shortlist (5 ideas)

### 1. Invoice/receipt extraction for freelancers and small bookkeepers — REJECT as standalone
- Users: freelancers, small businesses, bookkeepers. Problem: manual data entry. Evidence: independent per-invoice hour figures are scarce; most are vendor blogs. A 2013 Baseware survey (558 owners) found ~16.9 h/month on finance tasks in general ([eWeek](https://www.eweek.com/small-business/small-businesses-wasting-time-resources-on-manual-invoicing/)).
- Competitors: Dext (~£24/mo for 250 docs), Hubdoc (bundled with Xero), Veryfi (developer-oriented; paid tiers reported) ([comparison](https://accounts-os.com/blog/dext-alternatives-receipt-scanning-uk)). Free/local: [TaxHacker](https://github.com/vas3k/TaxHacker) (MIT, ~6.8k stars, Ollama support, receipts/invoices/bank statements), [Paperless-AI](https://cdn.jsdelivr.net/gh/clusterzx/paperless-ai@main/README.md) (MIT, ~5.5k stars, unconfirmed count).
- AI vs non-AI: LLM beats regex on receipts (SROIE F1 37–62% LLM vs 8–34% regex, [benchmark](https://imagetotable.ai/references/regex-vs-llm-field-extraction), receipts not invoices). So AI is justified, but...
- Verdict: **reject.** Free, mature, local-capable competitors already exist. Differentiation would be marginal. Revisit only if a distinct angle emerges.

### 2. Subscription price-creep detector from bank CSVs — REJECT (AI fails the baseline test)
- Problem is real but solvable with recurring-pattern detection and a rolling baseline plus threshold. Sources found no AI necessity; the open-source `monarch-mcp` recurring scan does it with rules ([source](https://docs.rs/crate/monarch-mcp/0.3.0/source/src/recurring_scan.rs)). Commercial: Origin, Rocket Money, SubTracker.
- AI could only help with merchant-name normalization, which fuzzy matching largely covers. Verdict: **reject** per rule 5.

### 3. Lease clause extraction and red-flag summary for small landlords/tenants — HOLD (backup)
- AI role: evidence-grounded extraction (quote + page) of key clauses. Small local models are mediocre: a 4B Gemma via Ollama got Exact Match 0.744, Token F1 0.505 with iterative retrieval on CUAD ([TU Delft thesis](https://repository.tudelft.nl/record/uuid:1cca8afa-7aae-425c-9d06-ce98dce177b9)). Larger cloud models reached only ~0.66 precision / 0.77 recall ([UFPE thesis](https://attena.ufpe.br/bitstream/123456789/58332/1/TCC%20Weybson%20Alves%20da%20Silva.pdf)).
- Lease benchmark: 179 annotated leases, but licence is CC BY-NC-SA 4.0, so it can't back a product ([arXiv](https://arxiv.org/abs/2010.10386v1)).
- Risks: perceived legal advice, hallucinated clauses, weak small-model quality. No demand evidence gathered. Verdict: **hold**; needs a retrieval-quality bake-off first.

### 4. Support-ticket triage for small teams using open-source helpdesks — HOLD (weak)
- Evidence: tiny tutorial test on 40 tickets, LoRA raised exact match 27.5%→80% ([source](https://labuladong.online/en/ai-coding/llm/lora-fine-tuning/), illustrative only). "Rules stall at 40–50%" is a vendor claim, **UNVERIFIED**. No independent benchmark found.
- Needs labelled tickets (which I don't have; privacy). Target users unclear. Verdict: **hold**, low priority.

### 5. Provider-bill vs EOB reconciliation for patients (local/private) — RECOMMENDED CANDIDATE (conditional)
- Users: US patients and family caregivers disputing medical bills.
- Severity/demand (secondary sources only): 2024 Commonwealth Fund survey, 45% of insured workers got a bill they thought insurance should cover; of those who disputed, 38% got it reduced or eliminated ([Drugs.com/HealthDay](https://www.drugs.com/news/common-medical-billing-errors-keep-many-americans-care-report-120561.html)). Only 30% felt extremely confident spotting an error ([Becker's](https://www.beckershospitalreview.com/capital/30-of-patients-feel-confident-to-identify-a-medical-billing-error)). Headline "80–90% of bills have errors" claims are advocacy/vendor numbers, 2013–2016 era ([KFF Health News](https://kffhealthnews.org/morning-breakout/studies-find-high-rates-of-errors-in-medical-billing/)); do not cite as fact.
- Competitors: many cheap apps ($10 one-time, $49/$149 reviews, contingency 25% of savings) incl. BillRx (claims browser-only, arithmetic/duplicate/EOB-mismatch checks) and medical-bill-defender ($49) ([search results](https://billrx.pages.dev/)). Vendor claims, unverified. Goodbill/MBAA pricing: **not found**.
- Existing alternative: call the insurer, hire an advocate, manual comparison.
- AI's specific role: extract line items (date, code, billed, allowed, patient responsibility) from heterogeneous scanned/photographed bills and EOBs, where templates fail. Detection itself is **deterministic** (arithmetic, duplicates, bill-vs-EOB patient-responsibility mismatch). This is honest: AI does extraction, rules do judgment.
- Differentiation (weak, to be tested): fully local, no PHI leaves the device; evidence-cited findings (each flag points to source text/region); no CPT bundling claims.
- Feasibility: moderate. OCR + small VLM/LLM on CPU is slow but batch-capable; accuracy on messy bills unknown.
- Cost: $0 operating. Hardware: CPU-only, unbenchmarked.
- Risks: crowded with cheap apps; stakes (wrong flag → bad dispute); CPT descriptions are AMA-licensed (use codes as opaque strings only); PHI, so tests use synthetic docs only; error prevalence uncertain.
- Portfolio value: good (privacy-first IDP + reconciliation + evaluation harness).
- Verdict: **candidate, not approved.** It survives only if it passes the non-AI baseline bake-off and the demand gates in `VALIDATION_PLAN.md`.

## Recommendation
One MVP: **Local Bill↔EOB Reconciler** (narrow scope below). Honest caveat: none of the five ideas has strong verified demand, and idea 5 is crowded by low-cost apps. The decision is provisional and the kill criteria in `VALIDATION_PLAN.md` are binding.

### MVP scope
- Input: one provider bill + one matching EOB (PDF/image, synthetic first). US only. English only.
- Output: structured line items + up to 4 deterministic flags (sum mismatch, duplicate line, EOB patient-responsibility ≠ billed patient amount, bill amount > EOB-allowed without adjustment), each with cited source snippet.
- Out of scope: CPT bundling/upcoding, appeal letters, negotiation, accounts, cloud, chat.

### Success criteria (measurable, to be set before building)
- Line-item field extraction F1 ≥ 0.90 on ≥ 30 synthetic + consented/own redacted docs, and ≥ 10 points better than the best non-AI baseline (OCR + regex/templates).
- Zero fabricated line items (flag any amount not found in OCR text).
- ≤ 3 min per document pair on this CPU.
- ≥ 5 real target users (recruited honestly) say they would use it, and ≥ 3 complete a task unaided.

### Free-first stack (candidates, none benchmarked here)
- Python 3.13, SQLite/files, local web UI (Streamlit/FastAPI).
- OCR: PaddleOCR / Tesseract; document parsing: Docling or PaddleOCR-VL (0.9B, [paper](https://arxiv.org/pdf/2510.14528)). Docling reported weaker on line items/tax (63% overall, secondary summary) ([summary](https://aitopics.org/doc/arxivorg:9D372157)).
- LLM: Qwen2.5/3 3–7B Q4 via llama.cpp or Ollama (install required; not present now). Constrained JSON output; validation in plain Python.
- Tests: pytest, synthetic generator, `gitleaks`/`pip-audit` before any push.

## Remaining research gaps
Competitor pricing for Goodbill/MBAA; primary source for 2024 JAMA claim; real CPU benchmarks; EOB format variability; legal/regulatory review of "bill review" claims; Reddit/forum demand (search returned none).
