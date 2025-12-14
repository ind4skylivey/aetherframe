"""Job schema — the fundamental unit of work in AetherFrame.

A Job represents a single analysis request against a target (binary, APK, PID).
Jobs flow through pipelines and accumulate Findings, Artifacts, and TraceEvents.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)

if TYPE_CHECKING:
    from pathlib import Path


class JobStatus(str, Enum):
    """Job lifecycle states."""
    pending = "pending"
    running = "running"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"


class TargetType(str, Enum):
    """Supported target types."""
    binary = "binary"
    apk = "apk"
    pid = "pid"
    memory_dump = "memory_dump"
    trace_log = "trace_log"


class JobCreate(BaseModel):
    """Schema for creating a new job."""
    target: str = Field(..., min_length=1, max_length=512, description="Path, PID, or identifier")
    target_type: TargetType = Field(default=TargetType.binary)
    pipeline_id: str = Field(default="quicklook", max_length=64)
    options: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_by: str = Field(default="anonymous", max_length=128)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "target": "/samples/suspicious.exe",
                "target_type": "binary",
                "pipeline_id": "deep-static",
                "options": {"skip_strings": False, "entropy_threshold": 7.0},
                "tags": ["malware", "packed"],
                "created_by": "analyst-1"
            }
        }
    )


class Job(BaseModel):
    """Complete job representation."""
    id: int
    target: str
    target_type: TargetType = TargetType.binary
    status: JobStatus = JobStatus.pending
    pipeline_id: str = "quicklook"
    current_stage: Optional[str] = None
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    options: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_by: str = "anonymous"
    created_at: datetime = Field(default_factory=_utc_now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "target": "/samples/suspicious.exe",
                "target_type": "binary",
                "status": "running",
                "pipeline_id": "deep-static",
                "current_stage": "umbriel",
                "progress": 35.0,
                "options": {},
                "tags": ["malware"],
                "created_by": "analyst-1",
                "created_at": "2025-12-13T21:00:00Z",
                "started_at": "2025-12-13T21:00:05Z"
            }
        }
    )


class JobContext(BaseModel):
    """Runtime context passed to plugins during execution.

    Contains everything a plugin needs to execute:
    - Job metadata
    - Target file path (resolved)
    - Workspace for intermediate files
    - Access to previous stage outputs
    """
    job: Job
    target_path: str  # Resolved absolute path
    workspace_dir: str  # Plugin scratch space
    artifacts_dir: str  # Where to write output artifacts
    previous_findings: List[Dict[str, Any]] = Field(default_factory=list)
    previous_artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    pipeline_context: Dict[str, Any] = Field(default_factory=dict)

    def get_artifact_path(self, filename: str) -> str:
        """Generate path for an output artifact."""
        from pathlib import Path
        return str(Path(self.artifacts_dir) / filename)

    def get_workspace_path(self, filename: str) -> str:
        """Generate path for a workspace file."""
        from pathlib import Path
        return str(Path(self.workspace_dir) / filename)
