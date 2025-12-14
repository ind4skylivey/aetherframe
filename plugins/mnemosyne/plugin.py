"""Mnemosyne — Memory and State Reconstruction Engine.

Mnemosyne consumes TraceEvents from LainTrace and other sources to:
- Reconstruct execution timelines
- Build state transition graphs
- Detect memory anomalies
- Track data flow through the program

Named after the Greek goddess of memory, Mnemosyne brings
order to the chaos of runtime events.
"""

from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

from aetherframe.plugins.base import Plugin, PluginManifest, PluginValidationError
from aetherframe.schemas import (
    JobContext, PluginResult,
    Finding, Severity, FindingCategory, Evidence,
    Artifact, ArtifactType,
    TraceEvent, TraceTimeline, EventSource, EventType
)


# ============================================================================
# STATE MODEL
# ============================================================================

class StateType(str, Enum):
    """Types of program states."""
    initial = "initial"
    running = "running"
    syscall = "syscall"
    library_call = "library_call"
    memory_op = "memory_op"
    exception = "exception"
    terminal = "terminal"


@dataclass
class ProgramState:
    """Represents a snapshot of program state at a point in time."""
    id: str
    timestamp: datetime
    state_type: StateType

    # Execution context
    address: Optional[str] = None
    symbol: Optional[str] = None
    thread_id: Optional[int] = None

    # Register snapshot (simplified)
    registers: Dict[str, int] = field(default_factory=dict)

    # Memory context
    stack_pointer: Optional[int] = None
    heap_allocations: int = 0

    # Metadata
    meta: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        """Generate a signature for state comparison."""
        sig = f"{self.state_type.value}:{self.symbol or self.address}"
        return hashlib.md5(sig.encode()).hexdigest()[:12]


@dataclass
class StateTransition:
    """A transition between two program states."""
    from_state: str  # State ID
    to_state: str  # State ID
    event_type: str
    timestamp: datetime
    duration_us: int = 0
    data: Dict[str, Any] = field(default_factory=dict)

    # For visualization
    label: str = ""
    weight: int = 1  # For collapsed transitions


@dataclass
class StateGraph:
    """Graph of program state transitions."""
    states: Dict[str, ProgramState] = field(default_factory=dict)
    transitions: List[StateTransition] = field(default_factory=list)
    initial_state: Optional[str] = None
    terminal_states: List[str] = field(default_factory=list)

    def add_state(self, state: ProgramState) -> None:
        """Add a state to the graph."""
        self.states[state.id] = state
        if state.state_type == StateType.initial and self.initial_state is None:
            self.initial_state = state.id
        if state.state_type == StateType.terminal:
            self.terminal_states.append(state.id)

    def add_transition(self, transition: StateTransition) -> None:
        """Add a transition to the graph."""
        self.transitions.append(transition)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "states": {
                sid: {
                    "id": s.id,
                    "type": s.state_type.value,
                    "symbol": s.symbol,
                    "address": s.address,
                    "thread_id": s.thread_id,
                    "timestamp": s.timestamp.isoformat()
                }
                for sid, s in self.states.items()
            },
            "transitions": [
                {
                    "from": t.from_state,
                    "to": t.to_state,
                    "type": t.event_type,
                    "label": t.label,
                    "weight": t.weight
                }
                for t in self.transitions
            ],
            "initial": self.initial_state,
            "terminal": self.terminal_states
        }

    def to_graphviz(self) -> str:
        """Generate GraphViz DOT representation."""
        lines = ["digraph StateGraph {"]
        lines.append("  rankdir=TB;")
        lines.append("  node [shape=box, style=rounded];")

        for sid, state in self.states.items():
            label = state.symbol or state.address or sid
            color = {
                StateType.initial: "green",
                StateType.terminal: "red",
                StateType.syscall: "orange",
                StateType.library_call: "blue",
                StateType.memory_op: "purple"
            }.get(state.state_type, "gray")
            lines.append(f'  "{sid}" [label="{label}", color={color}];')

        for t in self.transitions:
            label = t.label if t.label else t.event_type
            if t.weight > 1:
                label += f" (x{t.weight})"
            lines.append(f'  "{t.from_state}" -> "{t.to_state}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)


@dataclass
class Timeline:
    """Execution timeline built from trace events."""
    events: List[Dict[str, Any]] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: int = 0
    thread_timelines: Dict[int, List[Dict]] = field(default_factory=dict)

    def add_event(self, event: Dict[str, Any]) -> None:
        """Add an event to the timeline."""
        self.events.append(event)

        ts = event.get("timestamp")
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))

        if ts:
            if self.start_time is None or ts < self.start_time:
                self.start_time = ts
            if self.end_time is None or ts > self.end_time:
                self.end_time = ts

        # Track per-thread
        tid = event.get("thread_id", 0)
        if tid not in self.thread_timelines:
            self.thread_timelines[tid] = []
        self.thread_timelines[tid].append(event)

    def finalize(self) -> None:
        """Finalize timeline and compute stats."""
        if self.start_time and self.end_time:
            self.duration_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
        self.events.sort(key=lambda e: e.get("timestamp", ""))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "event_count": len(self.events),
            "thread_count": len(self.thread_timelines),
            "events": self.events
        }


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

@dataclass
class MemoryRegion:
    """Tracked memory region."""
    base: int
    size: int
    protection: str  # RWX
    allocation_time: datetime
    source: str  # Allocating function


class AnomalyDetector:
    """Detects memory and execution anomalies."""

    def __init__(self):
        self.allocations: Dict[int, MemoryRegion] = {}
        self.heap_spray_threshold = 100  # Same-size allocations
        self.same_size_counts: Dict[int, int] = defaultdict(int)
        self.stack_base: Optional[int] = None
        self.findings: List[Finding] = []

    def process_event(self, event: Dict[str, Any], job_id: UUID) -> Optional[Finding]:
        """Process an event and detect anomalies."""
        event_type = event.get("event_type", "")
        payload = event.get("payload", {})

        if event_type == "memory_alloc":
            return self._check_allocation(event, job_id)
        elif event_type == "memory_protect":
            return self._check_protection_change(event, job_id)
        elif event_type in ("hook_enter", "syscall_enter"):
            return self._check_suspicious_call(event, job_id)

        return None

    def _check_allocation(self, event: Dict[str, Any], job_id: UUID) -> Optional[Finding]:
        """Check for suspicious allocation patterns."""
        payload = event.get("payload", {})
        size = payload.get("size", 0)
        address = payload.get("address", 0)

        # Track same-size allocations (heap spray indicator)
        self.same_size_counts[size] += 1

        if self.same_size_counts[size] >= self.heap_spray_threshold:
            return Finding(
                job_id=job_id,
                severity=Severity.high,
                category=FindingCategory.heap_spray,
                title=f"Potential heap spray detected",
                description=f"{self.same_size_counts[size]} allocations of size {size}",
                evidence=[Evidence(
                    type="pattern",
                    value=f"size={size}, count={self.same_size_counts[size]}"
                )],
                confidence=0.75,
                tags=["mnemosyne", "heap-spray", "memory"]
            )

        return None

    def _check_protection_change(self, event: Dict[str, Any], job_id: UUID) -> Optional[Finding]:
        """Check for suspicious memory protection changes."""
        payload = event.get("payload", {})
        new_prot = payload.get("protection", "")
        address = payload.get("address", 0)

        # RWX is always suspicious
        if "rwx" in new_prot.lower() or (
            "w" in new_prot.lower() and "x" in new_prot.lower()
        ):
            return Finding(
                job_id=job_id,
                severity=Severity.high,
                category=FindingCategory.memory_anomaly,
                title="RWX memory region detected",
                description=f"Memory at 0x{address:x} changed to {new_prot}",
                evidence=[Evidence(
                    type="address",
                    location=f"0x{address:x}",
                    value=new_prot
                )],
                confidence=0.85,
                tags=["mnemosyne", "rwx", "shellcode"]
            )

        return None

    def _check_suspicious_call(self, event: Dict[str, Any], job_id: UUID) -> Optional[Finding]:
        """Check for suspicious function calls."""
        symbol = event.get("symbol", "")
        payload = event.get("payload", {})

        # Stack pivot detection
        if symbol in ("VirtualAlloc", "VirtualAllocEx", "mmap"):
            size = payload.get("args", [0])[0] if payload.get("args") else 0
            if size > 0x100000:  # >1MB allocation
                return Finding(
                    job_id=job_id,
                    severity=Severity.medium,
                    category=FindingCategory.memory_anomaly,
                    title=f"Large memory allocation: {symbol}",
                    description=f"Allocating {size} bytes via {symbol}",
                    evidence=[Evidence(
                        type="function",
                        location=symbol,
                        value=f"size={size}"
                    )],
                    confidence=0.6,
                    tags=["mnemosyne", "large-alloc"]
                )

        return None


# ============================================================================
# MNEMOSYNE PLUGIN
# ============================================================================

class MnemosynePlugin(Plugin):
    """Mnemosyne State Reconstruction Plugin.

    Consumes TraceEvents and builds:
    - Execution timelines
    - State transition graphs
    - Memory anomaly findings
    """

    def validate(self, ctx: JobContext) -> None:
        """Validate that we have trace data to process."""
        # Mnemosyne can work with:
        # 1. Previous stage events (from pipeline context)
        # 2. Trace log file
        # 3. Direct TraceEvent list

        has_events = bool(ctx.previous_artifacts) or bool(ctx.pipeline_context.get("trace_events"))
        has_trace_file = Path(ctx.target_path).suffix in (".json", ".trace", ".log")

        if not has_events and not has_trace_file:
            # It's okay, we might get events from LainTrace in the pipeline
            pass

    def run(self, ctx: JobContext) -> PluginResult:
        """Execute state reconstruction."""
        import time
        start_time = time.time()

        findings: List[Finding] = []
        artifacts: List[Artifact] = []
        events: List[TraceEvent] = []

        build_timeline = self.config.get("build_timeline", True)
        build_graph = self.config.get("build_graph", True)
        detect_anomalies = self.config.get("detect_anomalies", True)
        max_events = self.config.get("max_events", 10000)
        collapse_loops = self.config.get("collapse_loops", True)

        # Collect trace events from various sources
        trace_events = self._collect_events(ctx, max_events)

        if not trace_events:
            # Generate synthetic events from static analysis
            events.append(TraceEvent(
                job_id=ctx.job.id,
                source=EventSource.mnemosyne,
                event_type=EventType.warning,
                payload={"message": "No trace events available, using static analysis"}
            ))
            trace_events = self._generate_synthetic_events(ctx)

        # Build timeline
        timeline = None
        if build_timeline:
            timeline = self._build_timeline(trace_events)
            timeline.finalize()

            timeline_artifact = self._save_timeline(ctx, timeline)
            artifacts.append(timeline_artifact)

        # Build state graph
        state_graph = None
        if build_graph:
            state_graph = self._build_state_graph(trace_events, collapse_loops)

            graph_artifact = self._save_state_graph(ctx, state_graph)
            artifacts.append(graph_artifact)

            # Save GraphViz DOT
            dot_artifact = self._save_graphviz(ctx, state_graph)
            artifacts.append(dot_artifact)

        # Detect anomalies
        if detect_anomalies:
            detector = AnomalyDetector()
            for event in trace_events:
                finding = detector.process_event(event, ctx.job.id)
                if finding:
                    findings.append(finding)

        # Generate summary finding
        findings.append(Finding(
            job_id=ctx.job.id,
            severity=Severity.info,
            category=FindingCategory.state_transition,
            title=f"State reconstruction complete: {len(trace_events)} events",
            description=f"Timeline: {timeline.duration_ms}ms, States: {len(state_graph.states) if state_graph else 0}",
            evidence=[Evidence(
                type="pattern",
                value=json.dumps({
                    "events": len(trace_events),
                    "states": len(state_graph.states) if state_graph else 0,
                    "transitions": len(state_graph.transitions) if state_graph else 0,
                    "threads": len(timeline.thread_timelines) if timeline else 0
                })
            )],
            confidence=1.0,
            tags=["mnemosyne", "summary"]
        ))

        execution_time = int((time.time() - start_time) * 1000)

        return PluginResult(
            findings=findings,
            artifacts=artifacts,
            events=events,
            success=True,
            execution_time_ms=execution_time,
            context_data={
                "timeline_duration_ms": timeline.duration_ms if timeline else 0,
                "state_count": len(state_graph.states) if state_graph else 0,
                "transition_count": len(state_graph.transitions) if state_graph else 0,
                "anomaly_count": len([f for f in findings if f.severity in (Severity.high, Severity.critical)])
            }
        )

    def _collect_events(self, ctx: JobContext, max_events: int) -> List[Dict[str, Any]]:
        """Collect trace events from all available sources."""
        events = []

        # From pipeline context (LainTrace output)
        if "trace_events" in ctx.pipeline_context:
            events.extend(ctx.pipeline_context["trace_events"][:max_events])

        # From previous artifacts (look for trace files)
        for artifact in ctx.previous_artifacts:
            if artifact.get("artifact_type") == "trace" or "trace" in artifact.get("name", "").lower():
                uri = artifact.get("uri", "")
                if uri.startswith("file://"):
                    path = Path(uri[7:])
                    if path.exists():
                        try:
                            with open(path) as f:
                                data = json.load(f)
                                if isinstance(data, list):
                                    events.extend(data[:max_events - len(events)])
                                elif "events" in data:
                                    events.extend(data["events"][:max_events - len(events)])
                        except Exception:
                            pass

        # From target file if it's a trace log
        target = Path(ctx.target_path)
        if target.suffix in (".json", ".trace", ".log"):
            try:
                with open(target) as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        events.extend(data[:max_events - len(events)])
                    elif "events" in data:
                        events.extend(data["events"][:max_events - len(events)])
            except Exception:
                pass

        return events[:max_events]

    def _generate_synthetic_events(self, ctx: JobContext) -> List[Dict[str, Any]]:
        """Generate synthetic events from static analysis (fallback)."""
        # This is a placeholder - in production, would use static analysis
        # to generate a hypothetical execution trace
        return [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "state_init",
                "source": "mnemosyne",
                "symbol": "main",
                "payload": {"synthetic": True}
            }
        ]

    def _build_timeline(self, events: List[Dict[str, Any]]) -> Timeline:
        """Build execution timeline from events."""
        timeline = Timeline()

        for event in events:
            timeline.add_event({
                "timestamp": event.get("ts", event.get("timestamp")),
                "event_type": event.get("event_type", "unknown"),
                "source": event.get("source", "unknown"),
                "symbol": event.get("symbol"),
                "address": event.get("address"),
                "thread_id": event.get("thread_id", 0),
                "payload": event.get("payload", {})
            })

        return timeline

    def _build_state_graph(self, events: List[Dict[str, Any]], collapse: bool) -> StateGraph:
        """Build state transition graph from events."""
        graph = StateGraph()

        # Create initial state
        initial = ProgramState(
            id="state_0",
            timestamp=datetime.utcnow(),
            state_type=StateType.initial,
            symbol="_start"
        )
        graph.add_state(initial)

        current_state = initial
        state_counter = 1
        transition_cache: Dict[str, StateTransition] = {}

        for event in events:
            event_type = event.get("event_type", "")
            symbol = event.get("symbol", "")
            address = event.get("address", "")

            # Determine new state type
            if "syscall" in event_type:
                state_type = StateType.syscall
            elif "hook" in event_type or "call" in event_type:
                state_type = StateType.library_call
            elif "memory" in event_type:
                state_type = StateType.memory_op
            else:
                state_type = StateType.running

            # Create new state
            new_state = ProgramState(
                id=f"state_{state_counter}",
                timestamp=datetime.utcnow(),
                state_type=state_type,
                symbol=symbol or None,
                address=address or None,
                thread_id=event.get("thread_id")
            )

            # Check for collapse
            if collapse:
                sig = new_state.signature()
                existing = next(
                    (s for s in graph.states.values() if s.signature() == sig),
                    None
                )
                if existing:
                    # Find or create transition
                    trans_key = f"{current_state.id}->{existing.id}"
                    if trans_key in transition_cache:
                        transition_cache[trans_key].weight += 1
                    else:
                        trans = StateTransition(
                            from_state=current_state.id,
                            to_state=existing.id,
                            event_type=event_type,
                            timestamp=datetime.utcnow(),
                            label=symbol or event_type,
                            weight=1
                        )
                        graph.add_transition(trans)
                        transition_cache[trans_key] = trans
                    current_state = existing
                    continue

            graph.add_state(new_state)

            # Create transition
            trans = StateTransition(
                from_state=current_state.id,
                to_state=new_state.id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                label=symbol or event_type
            )
            graph.add_transition(trans)

            current_state = new_state
            state_counter += 1

        return graph

    def _save_timeline(self, ctx: JobContext, timeline: Timeline) -> Artifact:
        """Save timeline artifact."""
        path = ctx.get_artifact_path("state_timeline.json")
        with open(path, "w") as f:
            json.dump(timeline.to_dict(), f, indent=2, default=str)

        return Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.timeline,
            name="state_timeline.json",
            description="Execution timeline",
            uri=f"file://{path}",
            meta={
                "duration_ms": timeline.duration_ms,
                "event_count": len(timeline.events)
            }
        )

    def _save_state_graph(self, ctx: JobContext, graph: StateGraph) -> Artifact:
        """Save state graph artifact."""
        path = ctx.get_artifact_path("state_graph.json")
        with open(path, "w") as f:
            json.dump(graph.to_dict(), f, indent=2)

        return Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.graph,
            name="state_graph.json",
            description="State transition graph",
            uri=f"file://{path}",
            meta={
                "states": len(graph.states),
                "transitions": len(graph.transitions)
            }
        )

    def _save_graphviz(self, ctx: JobContext, graph: StateGraph) -> Artifact:
        """Save GraphViz DOT artifact."""
        path = ctx.get_artifact_path("state_graph.dot")
        with open(path, "w") as f:
            f.write(graph.to_graphviz())

        return Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.graph,
            name="state_graph.dot",
            description="State graph in GraphViz DOT format",
            uri=f"file://{path}"
        )
