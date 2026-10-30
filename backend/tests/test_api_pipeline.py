from decimal import Decimal as D

from fastapi.testclient import TestClient

from app import deps
from app.core.checks import Bill, Eob, Line
from app.main import app
from app.pipeline import process_case
from app.repo import MemoryRepo
from app.storage import MemoryStorage


def make_client():
    repo, storage, queue = MemoryRepo(), MemoryStorage(), []
    app.dependency_overrides[deps.get_repo] = lambda: repo
    app.dependency_overrides[deps.get_storage] = lambda: storage
    app.dependency_overrides[deps.get_enqueue] = lambda: queue.append
    return TestClient(app), repo, storage, queue


def upload(client, bill_type="image/png"):
    return client.post("/api/cases", files={
        "bill": ("bill.png", b"x", bill_type), "eob": ("eob.png", b"y", "image/png")})


def test_create_case_stores_files_and_enqueues():
    client, repo, storage, queue = make_client()
    r = upload(client)
    assert r.status_code == 202
    cid = r.json()["id"]
    assert queue == [cid] and storage.get(f"{cid}/bill") == b"x"
    assert client.get(f"/api/cases/{cid}").json()["status"] == "queued"
    assert len(client.get("/api/cases").json()) == 1


def test_rejects_bad_type_and_missing_case():
    client, *_ = make_client()
    assert upload(client, "text/plain").status_code == 415
    assert client.get("/api/cases/nope").status_code == 404


def test_pipeline_flags_and_failure_path():
    client, repo, storage, _ = make_client()
    cid = upload(client).json()["id"]
    bill = Bill([Line("2026-01-01", "A", D("100.00"), "row1"),
                 Line("2026-01-01", "A", D("100.00"), "row2")], D("200.00"), D("90.00"))
    process_case(cid, repo, storage, lambda *a: (bill, Eob([], D("40.00"))))
    case = repo.get(cid)
    assert case["status"] == "done"
    assert {f["kind"] for f in case["flags"]} == {"duplicate_line", "eob_mismatch"}

    def boom(*a):
        raise RuntimeError("quota")
    process_case(cid, repo, storage, boom)
    assert repo.get(cid)["status"] == "failed" and "quota" in repo.get(cid)["error"]
