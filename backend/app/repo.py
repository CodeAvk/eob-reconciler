from datetime import datetime, timezone
from typing import Protocol


class Repo(Protocol):
    def create(self, doc: dict) -> None: ...
    def get(self, case_id: str): ...
    def update(self, case_id: str, fields: dict) -> None: ...
    def list(self, limit: int = 50) -> list: ...


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MemoryRepo:
    def __init__(self):
        self.docs = {}

    def create(self, doc):
        self.docs[doc["id"]] = dict(doc)

    def get(self, case_id):
        d = self.docs.get(case_id)
        return dict(d) if d else None

    def update(self, case_id, fields):
        self.docs[case_id].update(fields)

    def list(self, limit=50):
        return sorted((dict(d) for d in self.docs.values()),
                      key=lambda d: d["created_at"], reverse=True)[:limit]


class MongoRepo:
    def __init__(self):
        from pymongo import MongoClient
        from app.config import settings
        self.col = MongoClient(settings.mongo_url)[settings.mongo_db]["cases"]
        self.col.create_index("created_at")

    def create(self, doc):
        self.col.insert_one({"_id": doc["id"], **doc})

    def get(self, case_id):
        return self.col.find_one({"_id": case_id}, {"_id": 0})

    def update(self, case_id, fields):
        self.col.update_one({"_id": case_id}, {"$set": fields})

    def list(self, limit=50):
        return list(self.col.find({}, {"_id": 0}).sort("created_at", -1).limit(limit))
