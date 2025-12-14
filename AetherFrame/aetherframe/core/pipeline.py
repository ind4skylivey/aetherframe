"""Pipeline definitions and execution engine.

Pipelines orchestrate plugin execution in defined sequences.
Each pipeline defines:
- Stage sequence
- Data flow between stages
- Failure handling
- Output aggregation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID
import logging
import time

from aetherframe.schemas import (
    Job, JobStatus, JobContext, PluginResult,
    Finding, Artifact, TraceEvent, EventSource, EventType
)
from aetherframe.plugins.registry import get_registry

logger = logging.getLogger(__name__)


class StageCondition(str, Enum):
    """Conditions for stage execution."""
    always = "always"
    on_success = "on_success"
    on_failure = "on_failure"
    on_findings = "on_findings"
    on_high_risk = "on_high_risk"
    conditional = "conditional"


@dataclass
class PipelineStage:
    """A single stage in a pipeline."""
    name: str
    plugin_id: str
    config: Dict[str, Any] = field(default_factory=dict)
    condition: StageCondition = StageCondition.on_success
    condition_expr: Optional[str] = None  # For conditional stages
    timeout_seconds: int = 300
    optional: bool = False  # If True, failures don't stop pipeline


@dataclass
class Pipeline:
    """Complete pipeline definition."""
    id: str
    name: str
    description: str
    stages: List[PipelineStage] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def add_stage(
        self,
        name: str,
        plugin_id: str,
        config: Optional[Dict[str, Any]] = None,
        condition: StageCondition = StageCondition.on_success,
        optional: bool = False
    ) -> "Pipeline":
        """Add a stage to the pipeline (builder pattern)."""
        self.stages.append(PipelineStage(
            name=name,
            plugin_id=plugin_id,
            config=config or {},
            condition=condition,
            optional=optional
        ))
        return self


# ============================================================================
# PREDEFINED PIPELINES
# ============================================================================

PIPELINES: Dict[str, Pipeline] = {}


def _register_builtin_pipelines():
    """Register the built-in pipelines."""

    # QUICKLOOK: Fast triage pipeline
    PIPELINES["quicklook"] = Pipeline(
        id="quicklook",
        name="Quicklook",
        description="Fast triage: Umbriel gate → Static summary → Noema intent",
        tags=["fast", "triage"]
    ).add_stage(
        name="gate",
        plugin_id="umbriel",
        config={"mode": "fast", "skip_entropy": False},
        condition=StageCondition.always
    ).add_stage(
        name="static",
        plugin_id="static_analyzer",
        optional=True
    ).add_stage(
        name="intent",
        plugin_id="noema",
        config={"depth": "shallow"}
    )

    # DEEP-STATIC: Comprehensive static analysis
    PIPELINES["deep-static"] = Pipeline(
        id="deep-static",
        name="Deep Static",
        description="Full static: Static → Umbriel → Noema deep",
        tags=["thorough", "static"]
    ).add_stage(
        name="static",
        plugin_id="static_analyzer",
        config={"extract_strings": True, "compute_entropy": True},
        condition=StageCondition.always
    ).add_stage(
        name="anti-analysis",
        plugin_id="umbriel",
        config={"mode": "thorough"}
    ).add_stage(
        name="intent",
        plugin_id="noema",
        config={"depth": "deep", "explain": True}
    )

    # DYNAMIC-FIRST: Dynamic analysis focused
    PIPELINES["dynamic-first"] = Pipeline(
        id="dynamic-first",
        name="Dynamic First",
        description="Dynamic: Umbriel → LainTrace → Mnemosyne → Noema",
        tags=["dynamic", "tracing"]
    ).add_stage(
        name="gate",
        plugin_id="umbriel",
        config={"mode": "fast"},
        condition=StageCondition.always
    ).add_stage(
        name="trace",
        plugin_id="laintrace",
        config={"profile": "strict", "timeout": 60}
    ).add_stage(
        name="reconstruct",
        plugin_id="mnemosyne",
        config={"build_timeline": True, "build_graph": True}
    ).add_stage(
        name="intent",
        plugin_id="noema",
        config={"depth": "deep", "use_traces": True}
    )

    # RELEASE-WATCH: Binary diff and evolution tracking
    PIPELINES["release-watch"] = Pipeline(
        id="release-watch",
        name="Release Watch",
        description="Diff: Valkyrie → Risk Score → Optional LainTrace → Noema",
        tags=["diff", "evolution"]
    ).add_stage(
        name="diff",
        plugin_id="valkyrie",
        config={"semantic": True, "generate_heatmap": True},
        condition=StageCondition.always
    ).add_stage(
        name="risk-score",
        plugin_id="valkyrie",
        config={"compute_risk": True},
        condition=StageCondition.on_success
    ).add_stage(
        name="trace-deltas",
        plugin_id="laintrace",
        config={"focus_changed_functions": True},
        condition=StageCondition.on_high_risk,
        optional=True
    ).add_stage(
        name="intent",
        plugin_id="noema",
        config={"analyze_diff": True}
    )

    # FULL-AUDIT: Everything
    PIPELINES["full-audit"] = Pipeline(
        id="full-audit",
        name="Full Audit",
        description="Complete analysis with all modules",
        tags=["complete", "audit"]
    ).add_stage(
        name="gate",
        plugin_id="umbriel",
        config={"mode": "thorough"},
        condition=StageCondition.always
    ).add_stage(
        name="static",
        plugin_id="static_analyzer"
    ).add_stage(
        name="trace",
        plugin_id="laintrace",
        config={"profile": "comprehensive"}
    ).add_stage(
        name="reconstruct",
        plugin_id="mnemosyne"
    ).add_stage(
        name="intent",
        plugin_id="noema",
        config={"depth": "deep", "explain": True}
    )


_register_builtin_pipelines()


# ============================================================================
# PIPELINE EXECUTOR
# ============================================================================

@dataclass
class PipelineExecutionResult:
    """Result of executing a complete pipeline."""
    job_id: UUID
    pipeline_id: str
    success: bool
    stages_executed: List[str]
    stages_skipped: List[str]
    stages_failed: List[str]
    total_findings: List[Finding]
    total_artifacts: List[Artifact]
    total_events: List[TraceEvent]
    execution_time_ms: int
    error: Optional[str] = None
    risk_score: float = 0.0


class PipelineExecutor:
    """Executes pipelines against jobs."""

    def __init__(self, on_stage_complete: Optional[Callable] = None):
        self.registry = get_registry()
        self.on_stage_complete = on_stage_complete

    def execute(self, job: Job, pipeline_id: str, base_ctx: JobContext) -> PipelineExecutionResult:
        """Execute a pipeline for a job.

        Args:
            job: The job to execute
            pipeline_id: ID of pipeline to run
            base_ctx: Base job context

        Returns:
            PipelineExecutionResult with aggregated results
        """
        if pipeline_id not in PIPELINES:
            raise ValueError(f"Unknown pipeline: {pipeline_id}")

        pipeline = PIPELINES[pipeline_id]
        start_time = time.time()

        # Aggregators
        all_findings: List[Finding] = []
        all_artifacts: List[Artifact] = []
        all_events: List[TraceEvent] = []
        stages_executed: List[str] = []
        stages_skipped: List[str] = []
        stages_failed: List[str] = []
        running_context: Dict[str, Any] = {}
        last_result: Optional[PluginResult] = None
        max_risk = 0.0

        # Emit pipeline start event
        all_events.append(TraceEvent(
            job_id=job.id,
            source=EventSource.orchestrator,
            event_type=EventType.stage_start,
            payload={"pipeline": pipeline_id, "stages": [s.name for s in pipeline.stages]}
        ))

        for stage in pipeline.stages:
            # Check stage condition
            if not self._should_execute_stage(stage, last_result, running_context):
                stages_skipped.append(stage.name)
                logger.info(f"Skipping stage {stage.name}: condition not met")
                continue

            logger.info(f"Executing stage: {stage.name} ({stage.plugin_id})")

            try:
                # Get plugin instance
                plugin = self.registry.get_instance(stage.plugin_id, stage.config)

                # Build stage context
                ctx = JobContext(
                    job=job,
                    target_path=base_ctx.target_path,
                    workspace_dir=base_ctx.workspace_dir,
                    artifacts_dir=base_ctx.artifacts_dir,
                    previous_findings=[f.model_dump() for f in all_findings],
                    previous_artifacts=[a.model_dump() for a in all_artifacts],
                    pipeline_context=running_context
                )

                # Validate
                plugin.validate(ctx)

                # Execute
                result = plugin.run(ctx)

                # Annotate results with stage info
                for f in result.findings:
                    f.plugin_id = stage.plugin_id
                    f.stage = stage.name
                for a in result.artifacts:
                    a.plugin_id = stage.plugin_id
                    a.stage = stage.name

                # Aggregate
                all_findings.extend(result.findings)
                all_artifacts.extend(result.artifacts)
                all_events.extend(result.events)
                stages_executed.append(stage.name)

                # Update context
                running_context.update(result.context_data)
                if result.risk_score:
                    max_risk = max(max_risk, result.risk_score)
                    running_context["_risk_score"] = max_risk

                last_result = result

                # Emit stage complete event
                all_events.append(TraceEvent(
                    job_id=job.id,
                    source=EventSource.orchestrator,
                    event_type=EventType.stage_complete,
                    payload={
                        "stage": stage.name,
                        "plugin": stage.plugin_id,
                        "findings": len(result.findings),
                        "artifacts": len(result.artifacts)
                    }
                ))

                if self.on_stage_complete:
                    self.on_stage_complete(stage.name, result)

                # Check abort
                if result.skip_remaining:
                    logger.warning(f"Pipeline aborted by {stage.name}")
                    break

            except Exception as e:
                error_msg = f"Stage {stage.name} failed: {e}"
                logger.error(error_msg)
                stages_failed.append(stage.name)

                all_events.append(TraceEvent(
                    job_id=job.id,
                    source=EventSource.orchestrator,
                    event_type=EventType.stage_error,
                    payload={"stage": stage.name, "error": str(e)}
                ))

                if not stage.optional:
                    return PipelineExecutionResult(
                        job_id=job.id,
                        pipeline_id=pipeline_id,
                        success=False,
                        stages_executed=stages_executed,
                        stages_skipped=stages_skipped,
                        stages_failed=stages_failed,
                        total_findings=all_findings,
                        total_artifacts=all_artifacts,
                        total_events=all_events,
                        execution_time_ms=int((time.time() - start_time) * 1000),
                        error=f"Stage {stage.name} failed: {e}",
                        risk_score=max_risk
                    )

        execution_time = int((time.time() - start_time) * 1000)

        return PipelineExecutionResult(
            job_id=job.id,
            pipeline_id=pipeline_id,
            success=len(stages_failed) == 0,
            stages_executed=stages_executed,
            stages_skipped=stages_skipped,
            stages_failed=stages_failed,
            total_findings=all_findings,
            total_artifacts=all_artifacts,
            total_events=all_events,
            execution_time_ms=execution_time,
            risk_score=max_risk
        )

    def _should_execute_stage(
        self,
        stage: PipelineStage,
        last_result: Optional[PluginResult],
        context: Dict[str, Any]
    ) -> bool:
        """Determine if a stage should execute based on its condition."""
        if stage.condition == StageCondition.always:
            return True

        if last_result is None:
            return stage.condition == StageCondition.always

        if stage.condition == StageCondition.on_success:
            return last_result.success

        if stage.condition == StageCondition.on_failure:
            return not last_result.success

        if stage.condition == StageCondition.on_findings:
            return len(last_result.findings) > 0

        if stage.condition == StageCondition.on_high_risk:
            risk = context.get("_risk_score", 0)
            return risk >= 0.7

        if stage.condition == StageCondition.conditional and stage.condition_expr:
            try:
                return eval(stage.condition_expr, {"ctx": context, "result": last_result})
            except Exception:
                return False

        return True


def get_pipeline(pipeline_id: str) -> Pipeline:
    """Get a pipeline by ID."""
    if pipeline_id not in PIPELINES:
        raise KeyError(f"Unknown pipeline: {pipeline_id}")
    return PIPELINES[pipeline_id]


def list_pipelines() -> List[Pipeline]:
    """List all available pipelines."""
    return list(PIPELINES.values())
