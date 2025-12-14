"""Orchestrator — the central controller for job execution.

The orchestrator is responsible for:
- Receiving job requests
- Resolving pipelines
- Managing job lifecycle
- Persisting results
- Emitting events
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID
import logging
import shutil
import tempfile

from aetherframe.schemas import (
    Job, JobCreate, JobStatus, JobContext,
    Finding, Artifact, TraceEvent,
    PluginResult
)
from aetherframe.core.pipeline import (
    PipelineExecutor, PipelineExecutionResult, get_pipeline, list_pipelines
)

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    workspace_base: Path = Path(tempfile.gettempdir()) / "aetherframe"
    artifacts_base: Path = Path(tempfile.gettempdir()) / "aetherframe" / "artifacts"
    max_concurrent_jobs: int = 4
    default_pipeline: str = "quicklook"
    cleanup_workspace: bool = True


class Orchestrator:
    """Central controller for job execution.

    The orchestrator coordinates the entire analysis flow:
    1. Accept job submission
    2. Prepare workspace
    3. Select and execute pipeline
    4. Aggregate results
    5. Persist to storage
    6. Cleanup
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        persist_finding: Optional[Callable[[Finding], None]] = None,
        persist_artifact: Optional[Callable[[Artifact], None]] = None,
        persist_event: Optional[Callable[[TraceEvent], None]] = None,
        update_job: Optional[Callable[[Job], None]] = None
    ):
        self.config = config or OrchestratorConfig()
        self.config.workspace_base.mkdir(parents=True, exist_ok=True)
        self.config.artifacts_base.mkdir(parents=True, exist_ok=True)

        # Persistence callbacks
        self._persist_finding = persist_finding
        self._persist_artifact = persist_artifact
        self._persist_event = persist_event
        self._update_job = update_job

        # Job tracking
        self._active_jobs: Dict[UUID, Job] = {}

        self.executor = PipelineExecutor(on_stage_complete=self._on_stage_complete)

    def submit(self, request: JobCreate) -> Job:
        """Submit a new job for execution.

        Args:
            request: Job creation request

        Returns:
            Created job with ID
        """
        job = Job(
            target=request.target,
            target_type=request.target_type,
            pipeline_id=request.pipeline_id or self.config.default_pipeline,
            options=request.options,
            tags=request.tags,
            created_by=request.created_by
        )

        self._active_jobs[job.id] = job
        logger.info(f"Job submitted: {job.id} target={job.target} pipeline={job.pipeline_id}")

        return job

    def execute(self, job: Job) -> PipelineExecutionResult:
        """Execute a job synchronously.

        Args:
            job: Job to execute

        Returns:
            Pipeline execution result
        """
        # Update status
        job.status = JobStatus.running
        job.started_at = datetime.utcnow()
        if self._update_job:
            self._update_job(job)

        # Prepare workspace
        workspace_dir = self.config.workspace_base / str(job.id)
        artifacts_dir = self.config.artifacts_base / str(job.id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Resolve target path
            target_path = self._resolve_target(job.target, workspace_dir)

            # Build context
            ctx = JobContext(
                job=job,
                target_path=str(target_path),
                workspace_dir=str(workspace_dir),
                artifacts_dir=str(artifacts_dir)
            )

            # Execute pipeline
            result = self.executor.execute(job, job.pipeline_id, ctx)

            # Persist results
            self._persist_results(result)

            # Update job status
            job.status = JobStatus.done if result.success else JobStatus.failed
            job.completed_at = datetime.utcnow()
            job.error = result.error
            if self._update_job:
                self._update_job(job)

            return result

        except Exception as e:
            logger.exception(f"Job {job.id} failed: {e}")
            job.status = JobStatus.failed
            job.completed_at = datetime.utcnow()
            job.error = str(e)
            if self._update_job:
                self._update_job(job)
            raise

        finally:
            # Cleanup workspace (but keep artifacts)
            if self.config.cleanup_workspace and workspace_dir.exists():
                shutil.rmtree(workspace_dir, ignore_errors=True)

            # Remove from active jobs
            self._active_jobs.pop(job.id, None)

    def execute_async(self, job: Job) -> UUID:
        """Queue a job for async execution (via Celery).

        Returns:
            Job ID for status tracking
        """
        from aetherframe.core.tasks import process_job_task
        process_job_task.delay(str(job.id))
        return job.id

    def get_job(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID."""
        return self._active_jobs.get(job_id)

    def list_active_jobs(self) -> List[Job]:
        """List all active jobs."""
        return list(self._active_jobs.values())

    def cancel(self, job_id: UUID) -> bool:
        """Cancel a running job."""
        job = self._active_jobs.get(job_id)
        if job and job.status == JobStatus.running:
            job.status = JobStatus.cancelled
            if self._update_job:
                self._update_job(job)
            return True
        return False

    def _resolve_target(self, target: str, workspace: Path) -> Path:
        """Resolve target to an accessible path."""
        target_path = Path(target)

        # If already a valid file, use it
        if target_path.exists():
            return target_path

        # Could be a URL, PID, etc. - handle here
        # For now, assume it's a local path
        raise FileNotFoundError(f"Target not found: {target}")

    def _persist_results(self, result: PipelineExecutionResult) -> None:
        """Persist all results from pipeline execution."""
        if self._persist_finding:
            for finding in result.total_findings:
                try:
                    self._persist_finding(finding)
                except Exception as e:
                    logger.error(f"Failed to persist finding: {e}")

        if self._persist_artifact:
            for artifact in result.total_artifacts:
                try:
                    self._persist_artifact(artifact)
                except Exception as e:
                    logger.error(f"Failed to persist artifact: {e}")

        if self._persist_event:
            for event in result.total_events:
                try:
                    self._persist_event(event)
                except Exception as e:
                    logger.error(f"Failed to persist event: {e}")

    def _on_stage_complete(self, stage_name: str, result: PluginResult) -> None:
        """Callback when a pipeline stage completes."""
        logger.info(f"Stage {stage_name} complete: {result.to_summary()}")


# Global orchestrator instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


def configure_orchestrator(config: OrchestratorConfig) -> Orchestrator:
    """Configure and return the global orchestrator."""
    global _orchestrator
    _orchestrator = Orchestrator(config)
    return _orchestrator
