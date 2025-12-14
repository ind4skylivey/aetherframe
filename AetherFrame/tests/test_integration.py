"""Tests for full pipeline integration."""

import pytest
from pathlib import Path
from uuid import uuid4

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherframe.schemas import Job, JobContext, JobStatus, TargetType
from aetherframe.core.pipeline import (
    Pipeline, PipelineStage, PipelineExecutor,
    PIPELINES, get_pipeline, list_pipelines
)
from aetherframe.plugins.registry import PluginRegistry


class TestPipelineDefinitions:
    """Test pipeline definitions."""

    def test_quicklook_pipeline_exists(self):
        """Quicklook pipeline should be defined."""
        assert "quicklook" in PIPELINES
        pipeline = PIPELINES["quicklook"]
        assert len(pipeline.stages) >= 2

    def test_deep_static_pipeline_exists(self):
        """Deep static pipeline should be defined."""
        assert "deep-static" in PIPELINES

    def test_dynamic_first_pipeline_exists(self):
        """Dynamic first pipeline should be defined."""
        assert "dynamic-first" in PIPELINES

    def test_release_watch_pipeline_exists(self):
        """Release watch pipeline should be defined."""
        assert "release-watch" in PIPELINES

    def test_list_pipelines(self):
        """Should list all pipelines."""
        pipelines = list_pipelines()
        assert len(pipelines) >= 4

    def test_get_pipeline(self):
        """Should get pipeline by ID."""
        pipeline = get_pipeline("quicklook")
        assert pipeline.id == "quicklook"
        assert pipeline.name == "Quicklook"

    def test_get_unknown_pipeline_raises(self):
        """Should raise for unknown pipeline."""
        with pytest.raises(KeyError):
            get_pipeline("nonexistent")


class TestPipelineStages:
    """Test pipeline stage configuration."""

    def test_quicklook_has_umbriel_gate(self):
        """Quicklook should start with Umbriel gate."""
        pipeline = PIPELINES["quicklook"]
        first_stage = pipeline.stages[0]
        assert first_stage.plugin_id == "umbriel"
        assert first_stage.name == "gate"

    def test_quicklook_ends_with_noema(self):
        """Quicklook should end with Noema."""
        pipeline = PIPELINES["quicklook"]
        last_stage = pipeline.stages[-1]
        assert last_stage.plugin_id == "noema"

    def test_dynamic_first_includes_laintrace(self):
        """Dynamic first should include LainTrace."""
        pipeline = PIPELINES["dynamic-first"]
        plugin_ids = [s.plugin_id for s in pipeline.stages]
        assert "laintrace" in plugin_ids

    def test_dynamic_first_includes_mnemosyne(self):
        """Dynamic first should include Mnemosyne."""
        pipeline = PIPELINES["dynamic-first"]
        plugin_ids = [s.plugin_id for s in pipeline.stages]
        assert "mnemosyne" in plugin_ids

    def test_release_watch_has_valkyrie(self):
        """Release watch should have Valkyrie."""
        pipeline = PIPELINES["release-watch"]
        plugin_ids = [s.plugin_id for s in pipeline.stages]
        assert "valkyrie" in plugin_ids


class TestPipelineBuilder:
    """Test pipeline builder pattern."""

    def test_add_stage(self):
        """Should add stages via builder."""
        pipeline = Pipeline(
            id="test",
            name="Test",
            description="Test pipeline"
        ).add_stage(
            name="stage1",
            plugin_id="plugin1"
        ).add_stage(
            name="stage2",
            plugin_id="plugin2"
        )

        assert len(pipeline.stages) == 2
        assert pipeline.stages[0].name == "stage1"
        assert pipeline.stages[1].name == "stage2"

    def test_stage_config(self):
        """Should pass config to stages."""
        pipeline = Pipeline(
            id="test",
            name="Test",
            description="Test"
        ).add_stage(
            name="stage1",
            plugin_id="plugin1",
            config={"key": "value"}
        )

        assert pipeline.stages[0].config == {"key": "value"}


class TestPluginRegistry:
    """Test plugin registry functionality."""

    @pytest.fixture
    def registry(self, tmp_path):
        """Create a registry with test plugins."""
        return PluginRegistry(plugins_dir=tmp_path)

    def test_discover_empty_dir(self, registry):
        """Should handle empty plugins directory."""
        discovered = registry.discover()
        assert len(discovered) == 0

    def test_list_plugins_empty(self, registry):
        """Should return empty list when no plugins."""
        plugins = registry.list_plugins()
        assert len(plugins) == 0

    def test_find_by_capability_empty(self, registry):
        """Should return empty for unknown capability."""
        found = registry.find_by_capability("unknown.capability")
        assert len(found) == 0


class TestDataFlow:
    """Test data flow through pipelines."""

    def test_context_accumulates_findings(self):
        """Previous findings should be available to later stages."""
        job = Job(
            id=1,
            target="/test",
            target_type=TargetType.binary,
            pipeline_id="quicklook"
        )

        ctx = JobContext(
            job=job,
            target_path="/test",
            workspace_dir="/tmp/ws",
            artifacts_dir="/tmp/art",
            previous_findings=[
                {"severity": "high", "category": "anti-debug", "title": "Test"}
            ]
        )

        assert len(ctx.previous_findings) == 1

    def test_context_accumulates_artifacts(self):
        """Previous artifacts should be available to later stages."""
        job = Job(
            id=2,
            target="/test",
            target_type=TargetType.binary,
            pipeline_id="quicklook"
        )

        ctx = JobContext(
            job=job,
            target_path="/test",
            workspace_dir="/tmp/ws",
            artifacts_dir="/tmp/art",
            previous_artifacts=[
                {"name": "report.json", "artifact_type": "json"}
            ]
        )

        assert len(ctx.previous_artifacts) == 1

    def test_pipeline_context_passed(self):
        """Pipeline context should be accessible."""
        job = Job(
            id=3,
            target="/test",
            target_type=TargetType.binary,
            pipeline_id="quicklook"
        )

        ctx = JobContext(
            job=job,
            target_path="/test",
            workspace_dir="/tmp/ws",
            artifacts_dir="/tmp/art",
            pipeline_context={"has_anti_debug": True, "risk_score": 0.8}
        )

        assert ctx.pipeline_context["has_anti_debug"] is True
        assert ctx.pipeline_context["risk_score"] == 0.8
