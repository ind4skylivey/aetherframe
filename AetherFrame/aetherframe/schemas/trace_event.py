"""TraceEvent schema — real-time events from dynamic analysis.

TraceEvents are the heartbeat of dynamic analysis:
- Hook triggers from Frida/LainTrace
- State changes from Mnemosyne
- Metrics from runtime monitoring
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class EventSource(str, Enum):
    """Event source modules."""
    laintrace = "laintrace"
    mnemosyne = "mnemosyne"
    umbriel = "umbriel"
    valkyrie = "valkyrie"
    noema = "noema"
    orchestrator = "orchestrator"
    plugin = "plugin"


class EventType(str, Enum):
    """Event type classification."""
    # Hooks
    hook_enter = "hook_enter"
    hook_exit = "hook_exit"
    hook_replace = "hook_replace"
    # State
    state_init = "state_init"
    state_change = "state_change"
    state_snapshot = "state_snapshot"
    # Memory
    memory_read = "memory_read"
    memory_write = "memory_write"
    memory_alloc = "memory_alloc"
    memory_free = "memory_free"
    memory_protect = "memory_protect"
    # Syscalls
    syscall_enter = "syscall_enter"
    syscall_exit = "syscall_exit"
    # Metrics
    metric_cpu = "metric_cpu"
    metric_memory = "metric_memory"
    metric_io = "metric_io"
    # Pipeline
    stage_start = "stage_start"
    stage_complete = "stage_complete"
    stage_error = "stage_error"
    # Generic
    info = "info"
    warning = "warning"
    error = "error"


class TraceEventCreate(BaseModel):
    """Schema for creating a trace event."""
    job_id: int
    source: EventSource
    event_type: EventType
    payload: Dict[str, Any] = Field(default_factory=dict)
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    address: Optional[str] = None  # Hex address if relevant
    symbol: Optional[str] = None  # Function/symbol name


class TraceEvent(BaseModel):
    """Complete trace event representation."""
    id: Optional[int] = None
    job_id: int
    ts: datetime = Field(default_factory=_utc_now)
    source: EventSource
    event_type: EventType
    payload: Dict[str, Any] = Field(default_factory=dict)
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    address: Optional[str] = None
    symbol: Optional[str] = None
    sequence: int = Field(default=0)  # For ordering within job
    meta: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "880e8400-e29b-41d4-a716-446655440003",
                "job_id": 123,
                "ts": "2025-12-13T21:00:10.123456Z",
                "source": "laintrace",
                "event_type": "hook_enter",
                "payload": {
                    "function": "CreateFileW",
                    "args": ["C:\\Windows\\System32\\config\\SAM", 0x80000000],
                    "return_address": "0x7ff712345678"
                },
                "thread_id": 1234,
                "process_id": 5678,
                "address": "0x7ff8abcd1234",
                "symbol": "kernel32!CreateFileW",
                "sequence": 42
            }
        }
    )


class TraceTimeline(BaseModel):
    """Aggregated timeline of trace events for a job."""
    job_id: int
    events: List[TraceEvent] = Field(default_factory=list)
    start_ts: Optional[datetime] = None
    end_ts: Optional[datetime] = None
    event_count: int = 0
    sources: List[EventSource] = Field(default_factory=list)

    def add_event(self, event: TraceEvent) -> None:
        """Add an event and update metadata."""
        self.events.append(event)
        self.event_count = len(self.events)
        if self.start_ts is None or event.ts < self.start_ts:
            self.start_ts = event.ts
        if self.end_ts is None or event.ts > self.end_ts:
            self.end_ts = event.ts
        if event.source not in self.sources:
            self.sources.append(event.source)

    def to_mnemosyne_format(self) -> Dict[str, Any]:
        """Export timeline in Mnemosyne-compatible format."""
        return {
            "job_id": str(self.job_id),
            "timeline": [
                {
                    "ts": e.ts.isoformat(),
                    "source": e.source.value,
                    "type": e.event_type.value,
                    "payload": e.payload
                }
                for e in sorted(self.events, key=lambda x: x.ts)
            ],
            "meta": {
                "start": self.start_ts.isoformat() if self.start_ts else None,
                "end": self.end_ts.isoformat() if self.end_ts else None,
                "count": self.event_count
            }
        }
