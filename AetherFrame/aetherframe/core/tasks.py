"""Celery tasks for job processing."""

from typing import Any, Dict

from aetherframe.core.celery_app import celery_app
from aetherframe.core import repository
from aetherframe.utils.db import get_session_factory
from aetherframe.core.models import JobStatus
from aetherframe.utils.license import enforce_or_fail_worker
import time

SessionLocal = get_session_factory()


@celery_app.task(name="aetherframe.process_job")
def process_job(job_id: int, target: str) -> Dict[str, Any]:
    """Execute analysis pipeline for a job."""
    enforce_or_fail_worker()

    # Import here to avoid potential circular imports during app startup
    from aetherframe.core.pipeline import PipelineExecutor
    from aetherframe.schemas import JobContext, Job as JobSchema
    from aetherframe.core.models import Job

    db = SessionLocal()
    try:
        # Fetch job to get pipeline_id
        db_job = db.query(Job).filter(Job.id == job_id).first()
        if not db_job:
            raise ValueError(f"Job {job_id} not found")

        pipeline_id = db_job.pipeline_id or "quicklook"
        repository.update_job_status(db, job_id, JobStatus.running)

        # Convert to Pydantic model
        job_schema = JobSchema.model_validate(db_job)

        # Initialize executor
        executor = PipelineExecutor()

        # Create base context
        # TODO: Configure workspace/artifacts dirs properly
        import tempfile
        from pathlib import Path

        workspace = Path(tempfile.gettempdir()) / "aetherframe" / str(job_id)
        artifacts_dir = workspace / "artifacts"
        workspace.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        ctx = JobContext(
            job=job_schema,
            target_path=target,
            workspace_dir=str(workspace),
            artifacts_dir=str(artifacts_dir)
        )

        # Execute pipeline
        result = executor.execute(job_schema, pipeline_id, ctx)

        # Update status
        status = JobStatus.completed if result.success else JobStatus.failed

        # Persist results
        # Findings and artifacts are already persisted by the executor/plugins?
        # Wait, PipelineExecutor aggregates them but does it persist them?
        # PipelineExecutor calls plugin.run() which returns PluginResult.
        # It does NOT persist them to DB automatically unless plugins do it?
        # Plugins return objects.
        # I need to persist them here!

        for finding in result.total_findings:
            repository.create_finding(db, finding)

        for artifact in result.total_artifacts:
            repository.create_artifact(db, artifact)

        for event in result.total_events:
            # Events might have been emitted already?
            # PipelineExecutor emits events to list.
            # I should persist them.
            repository.create_trace_event(db, event)

        final_result = {
            "pipeline_id": pipeline_id,
            "stages_executed": result.stages_executed,
            "stages_failed": result.stages_failed,
            "risk_score": result.risk_score,
            "execution_time_ms": result.execution_time_ms,
            "findings_count": len(result.total_findings),
            "artifacts_count": len(result.total_artifacts)
        }

        if result.error:
            final_result["error"] = result.error

        repository.update_job_status(db, job_id, status, final_result)

        return final_result

    except Exception as exc:
        fail_payload = {"error": str(exc), "ts": time.time()}
        repository.update_job_status(db, job_id, JobStatus.failed, fail_payload)
        repository.create_event(db, "job_failed", fail_payload, job_id)
        raise
    finally:
        db.close()
