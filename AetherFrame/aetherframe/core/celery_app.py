"""Celery application."""

from celery import Celery
from aetherframe.utils.config import get_settings

settings = get_settings()
BROKER_URL = f"redis://{settings.redis_host}:{settings.redis_port}/0"
BACKEND_URL = BROKER_URL

celery_app = Celery("aetherframe", broker=BROKER_URL, backend=BACKEND_URL)
# Register tasks
from aetherframe.core import tasks  # noqa: E402,F401


@celery_app.task
def ping() -> str:
    """Simple health task."""
    return "pong"
