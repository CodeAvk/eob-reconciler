from celery import Celery

from app.config import settings

celery_app = Celery("billrecon", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_acks_late = True


@celery_app.task(name="process_case")
def process_case_task(case_id: str):
    from app.deps import get_repo, get_storage
    from app.pipeline import process_case
    process_case(case_id, get_repo(), get_storage())
