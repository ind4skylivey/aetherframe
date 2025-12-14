# AetherFrame Release Roadmap

Status tracker for the early coding release and the remaining steps to reach a stable tag. (English only; keep in repo root `prompts/`.)

## Completed
- Docker/Podman conflict resolved; `DOCKER_HOST=unix:///var/run/docker.sock` documented and compose stacks start correctly.
- Core services up: API + Celery worker + Redis + Postgres + MinIO + UI (Vite preview) + CLI.
- API: root landing JSON, health/status/metrics endpoints, CORS for localhost, basic input trimming, Celery events (`job_started/completed/failed`) with elapsed time, Prometheus counters/gauges.
- Database: Alembic migrations applied for plugins, jobs, and events; migrations stored in repo.
- UI (Reveris Noctis): forms for plugins/jobs, dashboard with status/counts/jobs/events, auto-refresh, event wrapping, scrollable lists.
- CLI: Typer commands for add-plugin, add-job (shows recent events), list plugins/jobs/events, status; smoke-import in CI.
- CI: workflows for backend tests, CLI import, UI build; pytest configured with `PYTHONPATH=.`; docs updated with quickstart (compose + Alembic).
- Docs/Release: changelog and early tag `v0.1.0-early` recorded; architecture notes added.

## In Progress / Next
- Tests: expand API pytest coverage (validation errors, CORS preflight, metrics shape, job/event lifecycle with mocked Celery); add UI/API contract tests as feasible.
- Metrics hardening: ensure counters persist across restarts (DB-backed or init sync) and guard against divide-by-zero for averages.
- Config: make CORS origins/env-driven; document env surface (API, worker, UI).
- Security/Hardening: run worker container as non-root; optional request rate-limit; validate payload lengths/types; mention `vm.overcommit_memory=1` note for Redis.
- UI polish: add manual refresh + timestamps; keep event text clamped; loading states.
- CI guardrails: add Alembic “migrations up-to-date” check; keep backend/UI builds green; rerun after latest commits.
- Packaging/Release: produce next tagged pre-release after CI green; consider publishing images to GHCR (optional).

## Ready-to-ship checklist
- [ ] CI green (backend + UI + CLI).
- [ ] Tests cover validation, metrics, and job/event flow.
- [ ] CORS/config/env documented and configurable.
- [ ] Worker runs non-root; basic rate-limit/validation in place.
- [ ] README updated with latest quickstart (compose, Alembic, UI/CLI usage).
- [ ] Changelog entry for upcoming tag (e.g., `v0.1.0-preview`).
