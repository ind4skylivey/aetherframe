"""Tests for Umbriel anti-analysis detector plugin."""

import pytest
from pathlib import Path
from uuid import uuid4

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from aetherframe.schemas import (
    Job, JobContext, JobStatus, TargetType,
    Finding, Severity, FindingCategory
)
from aetherframe.plugins.umbriel.plugin import (
    UmbrielPlugin,
    calculate_entropy,
    ANTI_DEBUG_SIGNATURES,
    ANTI_VM_SIGNATURES
)
from aetherframe.plugins.base import PluginManifest, PluginKind


@pytest.fixture
def umbriel_manifest():
    """Create Umbriel manifest for testing."""
    return PluginManifest(
        id="umbriel",
        name="Umbriel",
        version="0.1.0",
        kind=PluginKind.detector,
        capabilities=["anti_analysis.scan"],
        inputs=["binary"],
        outputs=["findings", "artifacts"]
    )


@pytest.fixture
def umbriel_plugin(umbriel_manifest):
    """Create Umbriel plugin instance."""
    return UmbrielPlugin(umbriel_manifest, config={"mode": "thorough"})


@pytest.fixture
def test_job():
    """Create a test job."""
    return Job(
        id=uuid4(),
        target="/tmp/test.bin",
        target_type=TargetType.binary,
        status=JobStatus.running,
        pipeline_id="test"
    )


@pytest.fixture
def test_context(test_job, tmp_path):
    """Create a test job context."""
    # Create test binary with anti-debug patterns
    test_binary = tmp_path / "test.bin"
    test_binary.write_bytes(
        b"MZ" + b"\x00" * 100 +
        b"IsDebuggerPresent" +
        b"\x00" * 50 +
        b"VMware" +
        b"\x00" * 100
    )

    workspace = tmp_path / "workspace"
    workspace.mkdir()
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()

    return JobContext(
        job=test_job,
        target_path=str(test_binary),
        workspace_dir=str(workspace),
        artifacts_dir=str(artifacts)
    )


class TestUmbrielManifest:
    """Test Umbriel manifest validation."""

    def test_manifest_valid(self, umbriel_manifest):
        """Manifest should pass validation."""
        errors = umbriel_manifest.validate()
        assert len(errors) == 0

    def test_manifest_has_required_fields(self, umbriel_manifest):
        """Manifest should have all required fields."""
        assert umbriel_manifest.id == "umbriel"
        assert umbriel_manifest.name == "Umbriel"
        assert umbriel_manifest.kind == PluginKind.detector
        assert len(umbriel_manifest.capabilities) > 0


class TestEntropyCalculation:
    """Test entropy calculation functions."""

    def test_entropy_empty_data(self):
        """Empty data should have zero entropy."""
        assert calculate_entropy(b"") == 0.0

    def test_entropy_uniform_data(self):
        """Uniform data should have low entropy."""
        data = b"\x00" * 1000
        entropy = calculate_entropy(data)
        assert entropy == 0.0

    def test_entropy_random_data(self):
        """Random data should have high entropy."""
        import random
        random.seed(42)
        data = bytes(random.randint(0, 255) for _ in range(1000))
        entropy = calculate_entropy(data)
        assert entropy > 7.0

    def test_entropy_text_data(self):
        """Text data should have medium entropy."""
        data = b"The quick brown fox jumps over the lazy dog. " * 20
        entropy = calculate_entropy(data)
        assert 3.0 < entropy < 6.0


class TestAntiDebugDetection:
    """Test anti-debug pattern detection."""

    def test_detects_isdebugger_present(self, umbriel_plugin, test_context):
        """Should detect IsDebuggerPresent pattern."""
        result = umbriel_plugin.run(test_context)

        assert result.success
        anti_debug_findings = [
            f for f in result.findings
            if f.category == FindingCategory.anti_debug
        ]
        assert len(anti_debug_findings) > 0

        titles = [f.title for f in anti_debug_findings]
        assert any("IsDebuggerPresent" in t for t in titles)

    def test_detects_vmware(self, umbriel_plugin, test_context):
        """Should detect VMware string."""
        result = umbriel_plugin.run(test_context)

        anti_vm_findings = [
            f for f in result.findings
            if f.category == FindingCategory.anti_vm
        ]
        assert len(anti_vm_findings) > 0


class TestUmbrielPlugin:
    """Test Umbriel plugin execution."""

    def test_validation_passes(self, umbriel_plugin, test_context):
        """Validation should pass for valid context."""
        umbriel_plugin.validate(test_context)  # Should not raise

    def test_generates_findings(self, umbriel_plugin, test_context):
        """Should generate findings."""
        result = umbriel_plugin.run(test_context)
        assert len(result.findings) > 0

    def test_generates_artifacts(self, umbriel_plugin, test_context):
        """Should generate artifacts."""
        result = umbriel_plugin.run(test_context)
        assert len(result.artifacts) > 0

        artifact_names = [a.name for a in result.artifacts]
        assert "anti_analysis_report.json" in artifact_names

    def test_calculates_risk_score(self, umbriel_plugin, test_context):
        """Should calculate risk score."""
        result = umbriel_plugin.run(test_context)
        assert result.risk_score is not None
        assert 0 <= result.risk_score <= 1.0

    def test_provides_context_data(self, umbriel_plugin, test_context):
        """Should provide context data for next stages."""
        result = umbriel_plugin.run(test_context)

        assert "has_anti_debug" in result.context_data
        assert "has_anti_vm" in result.context_data
        assert "overall_entropy" in result.context_data

    def test_execution_time_tracked(self, umbriel_plugin, test_context):
        """Should track execution time."""
        result = umbriel_plugin.run(test_context)
        assert result.execution_time_ms is not None
        assert result.execution_time_ms >= 0


class TestSignatures:
    """Test signature definitions."""

    def test_anti_debug_signatures_defined(self):
        """Anti-debug signatures should be defined."""
        assert len(ANTI_DEBUG_SIGNATURES) > 0

    def test_anti_vm_signatures_defined(self):
        """Anti-VM signatures should be defined."""
        assert len(ANTI_VM_SIGNATURES) > 0

    def test_signatures_have_required_fields(self):
        """Signatures should have required fields."""
        for sig in ANTI_DEBUG_SIGNATURES + ANTI_VM_SIGNATURES:
            assert sig.id
            assert sig.name
            assert sig.category
            assert sig.severity
            assert sig.pattern
            assert 0 <= sig.confidence <= 1.0
