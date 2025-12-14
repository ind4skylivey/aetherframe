import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ.setdefault("AETHERFRAME_DB_URL", f"sqlite:///{TEST_DB}")
os.environ.setdefault("AETHERFRAME_LICENSE_ENFORCE", "false")
os.environ.setdefault("ENVIRONMENT", "test")
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aetherframe.utils.config import get_settings
get_settings.cache_clear()

from aetherframe.api.main import app
from aetherframe.utils import db as db_utils
from aetherframe.core.models import Base
from aetherframe.core.celery_app import celery_app


@pytest.fixture(scope="module")
def client():
    # Setup in-memory SQLite for fast tests
    engine = create_engine(os.environ["AETHERFRAME_DB_URL"], future=True)
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_session():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_utils.get_session] = override_get_session

    # Mock celery send_task to avoid redis
    celery_app.send_task = lambda *args, **kwargs: None

    with TestClient(app) as c:
        yield c


def test_create_plugin_and_job(client):
    resp = client.post("/plugins", json={"name": "p1", "version": "0.1.0", "description": "test"})
    assert resp.status_code == 200
    plugin_id = resp.json()["id"]

    resp = client.post("/jobs", json={"target": "sample.bin", "plugin_id": plugin_id})
    assert resp.status_code == 200
    job = resp.json()
    assert job["target"] == "sample.bin"
    assert job["plugin_id"] == plugin_id

    status = client.get("/status").json()
    assert status["metrics"]["jobs_total"] >= 1
    assert status["metrics"]["plugins_total"] >= 1


def test_validation_and_trim(client):
    # missing fields should 422
    resp = client.post("/plugins", json={"name": " ", "version": " "})
    assert resp.status_code == 422

    # trim inputs stored cleanly
    resp = client.post("/plugins", json={"name": "  spaced  ", "version": " 1.0.0 ", "description": "  desc "})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "spaced"
    assert data["version"] == "1.0.0"
    assert data["description"] == "desc"


def test_metrics_and_events(client):
    # create plugin/job
    plugin = client.post("/plugins", json={"name": "p-metric", "version": "0.2.0", "description": ""}).json()
    job = client.post("/jobs", json={"target": "metric.bin", "plugin_id": plugin["id"]}).json()

    # create events
    e1 = client.post("/events", json={"event_type": "job_started", "payload": {"target": job["target"]}, "job_id": job["id"]})
    assert e1.status_code == 200
    e2 = client.post("/events", json={"event_type": "job_completed", "payload": {"status": "ok"}, "job_id": job["id"]})
    assert e2.status_code == 200

    # status aggregates counts
    status = client.get("/status").json()
    assert status["metrics"]["events_total"] >= 2
    assert status["metrics"]["jobs_by_status"]["pending"] >= 0

    # metrics endpoint presents prometheus-style gauges
    text = client.get("/metrics").text
    assert "aether_jobs_total" in text
    assert 'aether_jobs_status_total{status="' in text


def test_cors_preflight(client):
    resp = client.options(
        "/plugins",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:3000"
