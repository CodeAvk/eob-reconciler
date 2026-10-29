from functools import lru_cache


@lru_cache
def get_repo():
    from app.repo import MongoRepo
    return MongoRepo()


@lru_cache
def get_storage():
    from app.storage import MinioStorage
    return MinioStorage()


def get_enqueue():
    from app.worker import process_case_task
    return process_case_task.delay
