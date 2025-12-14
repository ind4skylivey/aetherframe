# Changelog

## Unreleased
### Added
- Additional API tests covering validation, metrics, CORS preflight, and event flow.
- Configurable CORS origins via `AETHERFRAME_CORS_ORIGINS` env var.
- Configurable database URL via `AETHERFRAME_DB_URL`/`DB_URL` for testing.
- License enforcement hook (ed25519 token) for API/worker via `AETHERFRAME_LICENSE_TOKEN` and `AETHERFRAME_LICENSE_ENFORCE`.

## v0.1.0-early (2025-11-28)
### Added
- FastAPI backend with jobs/plugins CRUD, Celery tasks, events, metrics (`/status`, `/metrics`).
- Alembic migrations (plugins, jobs, events) and Prometheus-style gauges.
- Reveris Noctis UI (Vite React) with forms for plugins/jobs, dashboard and auto-refresh.
- Reveris Noctis CLI (Typer) with plugin/job/events commands.
- Docker Compose stack (API, worker, Redis, Postgres, MinIO, UI).
- CI: backend tests (pytest + httpx), CLI smoke, UI build.

### Changed
- Switched DB driver to psycopg3.
- CORS enabled for localhost UI; input validation/trim on API.
- Worker runs non-root; events emitted for job lifecycle.

### Notes
- Set `DOCKER_HOST=unix:///var/run/docker.sock` if your shell aliases docker to podman.
- Apply Alembic inside API container: `alembic upgrade head` with `PYTHONPATH=/app`.
