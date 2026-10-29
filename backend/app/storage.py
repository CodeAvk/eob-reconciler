import io
from typing import Protocol

from app.config import settings


class Storage(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...


class MemoryStorage:
    def __init__(self):
        self.objects = {}

    def put(self, key, data, content_type):
        self.objects[key] = data

    def get(self, key):
        return self.objects[key]


class MinioStorage:
    def __init__(self):
        from minio import Minio
        self.bucket = settings.minio_bucket
        self.client = Minio(settings.minio_endpoint, settings.minio_access_key,
                            settings.minio_secret_key, secure=settings.minio_secure)
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put(self, key, data, content_type):
        self.client.put_object(self.bucket, key, io.BytesIO(data), len(data),
                               content_type=content_type)

    def get(self, key):
        resp = self.client.get_object(self.bucket, key)
        try:
            return resp.read()
        finally:
            resp.close()
            resp.release_conn()
