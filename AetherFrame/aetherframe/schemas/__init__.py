"""AetherFrame unified schemas for the reverse engineering laboratory."""

from .job import Job, JobCreate, JobStatus, JobContext, TargetType
from .artifact import Artifact, ArtifactCreate, ArtifactType
from .finding import Finding, FindingCreate, Severity, FindingCategory, Evidence
from .trace_event import TraceEvent, TraceEventCreate, EventType, EventSource, TraceTimeline
from .plugin_result import PluginResult

__all__ = [
    # Job
    "Job",
    "JobCreate",
    "JobStatus",
    "JobContext",
    "TargetType",
    # Artifact
    "Artifact",
    "ArtifactCreate",
    "ArtifactType",
    # Finding
    "Finding",
    "FindingCreate",
    "Severity",
    "FindingCategory",
    "Evidence",
    # TraceEvent
    "TraceEvent",
    "TraceEventCreate",
    "EventType",
    "EventSource",
    "TraceTimeline",
    # Plugin
    "PluginResult",
]

