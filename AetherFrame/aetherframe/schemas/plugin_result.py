"""PluginResult schema — standardized output from all plugins.

Every plugin MUST return a PluginResult containing:
- findings: Security-relevant observations
- artifacts: Output files (reports, graphs, dumps)
- events: Runtime trace events (optional)
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from .finding import Finding
from .artifact import Artifact
from .trace_event import TraceEvent


class PluginResult(BaseModel):
    """Unified result structure returned by all plugins.

    This is the CONTRACT. All plugins MUST return this structure.
    The orchestrator uses this to:
    - Persist findings to DB
    - Upload artifacts to MinIO
    - Append events to timeline
    - Pass data to next pipeline stage
    """
    findings: List[Finding] = Field(default_factory=list)
    artifacts: List[Artifact] = Field(default_factory=list)
    events: List[TraceEvent] = Field(default_factory=list)

    # Execution metadata
    success: bool = True
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None

    # Pipeline control
    skip_remaining: bool = False  # If True, abort pipeline after this stage
    recommendations: List[str] = Field(default_factory=list)  # Suggested next actions
    risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)

    # Inter-stage data (passed to next plugin in pipeline)
    context_data: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "findings": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440002",
                        "job_id": "550e8400-e29b-41d4-a716-446655440000",
                        "severity": "high",
                        "category": "anti-debug",
                        "title": "IsDebuggerPresent API detected",
                        "confidence": 0.95
                    }
                ],
                "artifacts": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "job_id": "550e8400-e29b-41d4-a716-446655440000",
                        "artifact_type": "json",
                        "name": "anti_analysis_report.json"
                    }
                ],
                "events": [],
                "success": True,
                "execution_time_ms": 1234,
                "risk_score": 0.85,
                "recommendations": ["Consider dynamic analysis", "Check for VM detection"],
                "context_data": {"is_packed": True, "entropy": 7.8}
            }
        }
    )

    @property
    def finding_count(self) -> int:
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        from .finding import Severity
        return sum(1 for f in self.findings if f.severity == Severity.critical)

    @property
    def high_count(self) -> int:
        from .finding import Severity
        return sum(1 for f in self.findings if f.severity == Severity.high)

    def merge(self, other: "PluginResult") -> "PluginResult":
        """Merge another result into this one."""
        return PluginResult(
            findings=self.findings + other.findings,
            artifacts=self.artifacts + other.artifacts,
            events=self.events + other.events,
            success=self.success and other.success,
            error=self.error or other.error,
            execution_time_ms=(self.execution_time_ms or 0) + (other.execution_time_ms or 0),
            skip_remaining=self.skip_remaining or other.skip_remaining,
            recommendations=self.recommendations + other.recommendations,
            risk_score=max(self.risk_score or 0, other.risk_score or 0),
            context_data={**self.context_data, **other.context_data}
        )

    def to_summary(self) -> Dict[str, Any]:
        """Generate a summary for logging/display."""
        return {
            "success": self.success,
            "findings": self.finding_count,
            "critical": self.critical_count,
            "high": self.high_count,
            "artifacts": len(self.artifacts),
            "events": len(self.events),
            "risk_score": self.risk_score,
            "execution_time_ms": self.execution_time_ms
        }
