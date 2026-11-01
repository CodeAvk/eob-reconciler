# Bill Reconciler

A portfolio project that compares a medical provider bill with its insurance explanation of benefits (EOB) and flags differences, with each finding citing the text it came from.

**Status: working prototype, tested on synthetic documents only. User demand has not been validated.** It is not medical, legal or billing advice, and it should not be given real health records (see Privacy).

## What it does

1. You upload a bill and an EOB (image or PDF).
2. A Gemini vision model reads both and returns structured line items, totals and the patient amount.
3. Plain Python checks (no AI) look for three problems: line items that do not add up to the stated total, a charge that appears twice, and a bill that asks the patient for a different amount than the EOB says.
4. The result page shows each flag with the printed row it came from. Anything the model could not quote is labelled as reconstructed.

The AI does extraction only. Judging is deterministic, which keeps the findings explainable.

## How well does the AI part work?

Measured on 30 synthetic hard-mode cases (tilted, noisy, varied formats) against non-AI baselines using free OCR (RapidOCR) plus regex. Full detail and caveats are in [docs/GATE1_RESULTS.md](docs/GATE1_RESULTS.md).

| Extractor | Line F1 | Flags exactly right | False alarms on clean bills |
|---|---|---|---|
| OCR + regex | 0.697 | 63% | 6 of 8 |
| OCR + regex + deskew | 0.914 | 77% | 4 of 8 |
| Gemini 2.5 Flash | 0.970 | 100% | 0 of 8 |

Takeaways, stated plainly:

- On clean, uniform documents a free OCR + regex pipeline is already perfect, so AI is unnecessary there.
- On messy documents Gemini is clearly better at end-to-end accuracy, but its lead on line F1 over a decent baseline is only about 5.6 points. A more heavily engineered baseline could close more of the gap.
- Gemini sometimes silently altered a code (3 of 101 lines), which is why the UI asks users to verify against the original.
- Data is synthetic and the hard set was designed after seeing the easy one, so treat this as a stress test, not a real-world accuracy figure.

## Stack

- **Frontend:** Next.js 16, React 19, TypeScript, plain CSS, lucide icons. Responsive from phone to desktop, light and dark.
- **Backend:** FastAPI, Celery worker, Redis (queue), MongoDB (cases), MinIO (uploaded files).
- **AI:** Gemini API, free tier (about 20 requests per day, one request per case).
- **Baseline and evaluation:** RapidOCR, a synthetic document generator with known ground truth, and a scoring harness.

## Run it locally

Needs Python 3.13, Node 22, Docker and a free Gemini API key.

```
cp .env.example .env            # then set GEMINI_API_KEY (keep .env out of git)
docker compose up -d            # MongoDB, Redis (host port 6380), MinIO

cd backend
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m uvicorn app.main:app --port 8000
.venv/Scripts/python -m celery -A app.worker.celery_app worker --pool=solo --loglevel=info

cd ../frontend
npm install && npm run dev      # http://localhost:3000
```

If port 3000 is busy, run the web app on 3100 (`npx next start -p 3100`). The API already allows both origins; set `CORS_ORIGINS` to change them. On Linux or macOS use `.venv/bin/python` and drop `--pool=solo`.

Generate sample documents and run the evaluation:

```
cd backend
python -m app.synthetic ../data/generated/demo 8 1 hard
python -m app.evaluate ../data/generated/demo --extractor baseline_deskew
```

Tests: `cd backend && python -m pytest -q` (42 tests) and `cd frontend && npx tsc --noEmit`.

## Privacy

The free Gemini tier may retain and human-review submitted content, and Google's terms say not to submit sensitive or personal data. Use this project only with synthetic or fully redacted documents. Automatic redaction before the API call is planned but not built yet.

## Limits

- Free-tier quota caps use at roughly 20 cases per day.
- US medical bills only, English only, three checks only. No coding or bundling rules, no appeals, no accounts.
- Not tested on real documents.

## Repository guide

- `backend/app` : API, pipeline, extraction, checks, baseline, evaluation, synthetic data
- `frontend` : web app
- `docs/GATE1_RESULTS.md` : the AI-versus-baseline evaluation
- `PRODUCT_RESEARCH.md`, `VALIDATION_PLAN.md`, `PLAN.md` : research, plan and status
