"""Artifact schema — output files produced by plugins.

Artifacts are the tangible outputs of analysis:
- JSON reports
- HTML visualizations
- Memory dumps
- Diff graphs
- State timelines
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class ArtifactType(str, Enum):
    """Supported artifact types."""
    json = "json"
    html = "html"
    dump = "dump"
    graph = "graph"
    timeline = "timeline"
    heatmap = "heatmap"
    diff = "diff"
    report = "report"
    strings = "strings"
    disasm = "disasm"
    callgraph = "callgraph"
    state_snapshot = "state_snapshot"
    raw = "raw"


class ArtifactCreate(BaseModel):
    """Schema for creating an artifact."""
    job_id: int
    artifact_type: ArtifactType
    name: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(default=None, max_length=1024)
    content: Optional[Dict[str, Any]] = None  # Inline JSON content
    uri: Optional[str] = None  # External storage URI (MinIO/S3)
    sha256: Optional[str] = Field(default=None, min_length=64, max_length=64)
    size_bytes: Optional[int] = Field(default=None, ge=0)
    meta: Dict[str, Any] = Field(default_factory=dict)


class Artifact(BaseModel):
    """Complete artifact representation."""
    id: Optional[int] = None
    job_id: int
    artifact_type: ArtifactType
    name: str
    description: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    uri: Optional[str] = None  # s3://aether-artifacts/job-uuid/artifact.json
    sha256: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: datetime = Field(default_factory=_utc_now)
    plugin_id: Optional[str] = None  # Which plugin produced this
    stage: Optional[str] = None  # At which pipeline stage
    meta: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "job_id": 123,
                "artifact_type": "json",
                "name": "anti_analysis_report.json",
                "description": "Umbriel anti-analysis detection results",
                "uri": "s3://aether-artifacts/550e8400/anti_analysis_report.json",
                "sha256": "a" * 64,
                "size_bytes": 4096,
                "plugin_id": "umbriel",
                "stage": "gate",
                "meta": {"detections": 5, "risk_score": 0.85}
            }
        }
    )

    def is_inline(self) -> bool:
        """Check if artifact content is stored inline."""
        return self.content is not None

    def is_external(self) -> bool:
        """Check if artifact is stored externally."""
        return self.uri is not None
