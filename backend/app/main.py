import uuid

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.deps import get_enqueue, get_repo, get_storage
from app.repo import now

ALLOWED = {"image/png", "image/jpeg", "image/webp", "application/pdf"}

app = FastAPI(title="Bill Reconciler API")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health():
    return {"status": "ok"}


async def _read(upload: UploadFile) -> bytes:
    if upload.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported file type: {upload.content_type}")
    data = await upload.read()
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File larger than {settings.max_upload_mb} MB")
    if not data:
        raise HTTPException(400, "Empty file")
    return data


@app.post("/api/cases", status_code=202)
async def create_case(bill: UploadFile = File(...), eob: UploadFile = File(...),
                      repo=Depends(get_repo), storage=Depends(get_storage),
                      enqueue=Depends(get_enqueue)):
    bill_data, eob_data = await _read(bill), await _read(eob)
    case_id = uuid.uuid4().hex
    bill_key, eob_key = f"{case_id}/bill", f"{case_id}/eob"
    storage.put(bill_key, bill_data, bill.content_type)
    storage.put(eob_key, eob_data, eob.content_type)
    repo.create({"id": case_id, "status": "queued", "created_at": now(),
                 "updated_at": now(), "bill_key": bill_key, "eob_key": eob_key,
                 "bill_mime": bill.content_type, "eob_mime": eob.content_type,
                 "bill_name": bill.filename, "eob_name": eob.filename,
                 "flags": [], "error": None})
    enqueue(case_id)
    return {"id": case_id, "status": "queued"}


@app.get("/api/cases")
def list_cases(repo=Depends(get_repo)):
    return repo.list()


@app.get("/api/cases/{case_id}")
def get_case(case_id: str, repo=Depends(get_repo)):
    case = repo.get(case_id)
    if not case:
        raise HTTPException(404, "Case not found")
    return case
