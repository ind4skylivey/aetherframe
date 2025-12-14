"""Static Analyzer — Basic static analysis plugin."""

from __future__ import annotations
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from aetherframe.plugins.base import Plugin, PluginManifest, PluginValidationError
from aetherframe.schemas import (
    JobContext, PluginResult,
    Finding, Severity, FindingCategory, Evidence,
    Artifact, ArtifactType,
    TraceEvent, EventSource, EventType
)


def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy."""
    if not data:
        return 0.0
    counter = Counter(data)
    length = len(data)
    entropy = 0.0
    for count in counter.values():
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return entropy


def extract_strings(data: bytes, min_length: int = 6) -> List[str]:
    """Extract printable ASCII strings."""
    pattern = rb"[\x20-\x7e]{" + str(min_length).encode() + rb",}"
    matches = re.findall(pattern, data)
    return [m.decode("ascii", errors="ignore") for m in matches]


class StaticAnalyzerPlugin(Plugin):
    """Basic static analysis plugin."""

    def validate(self, ctx: JobContext) -> None:
        target = Path(ctx.target_path)
        if not target.exists():
            raise PluginValidationError(self.id, f"File not found: {target}")

    def run(self, ctx: JobContext) -> PluginResult:
        import time
        start = time.time()

        target = Path(ctx.target_path)
        data = target.read_bytes()

        findings: List[Finding] = []
        artifacts: List[Artifact] = []
        events: List[TraceEvent] = []

        # Config
        extract_str = self.config.get("extract_strings", True)
        compute_ent = self.config.get("compute_entropy", True)
        min_len = self.config.get("min_string_length", 6)

        # File info
        sha256 = hashlib.sha256(data).hexdigest()
        size = len(data)

        # Detect format
        fmt = "unknown"
        if data[:2] == b"MZ":
            fmt = "pe"
        elif data[:4] == b"\x7fELF":
            fmt = "elf"
        elif data[:4] in (b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe"):
            fmt = "macho"

        # Extract strings
        strings = []
        if extract_str:
            strings = extract_strings(data, min_len)[:500]

        # Compute entropy
        entropy = 0.0
        if compute_ent:
            entropy = calculate_entropy(data)

        # Create report
        report = {
            "plugin": "static_analyzer",
            "file": str(target),
            "sha256": sha256,
            "size": size,
            "format": fmt,
            "entropy": round(entropy, 4),
            "strings_count": len(strings),
            "strings_sample": strings[:50]
        }

        report_path = ctx.get_artifact_path("static_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        artifacts.append(Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.json,
            name="static_report.json",
            description="Static analysis report",
            uri=f"file://{report_path}"
        ))

        # Strings artifact
        if strings:
            strings_path = ctx.get_artifact_path("strings.txt")
            with open(strings_path, "w") as f:
                f.write("\n".join(strings))

            artifacts.append(Artifact(
                job_id=ctx.job.id,
                artifact_type=ArtifactType.strings,
                name="strings.txt",
                description="Extracted strings",
                uri=f"file://{strings_path}"
            ))

        # Basic finding
        findings.append(Finding(
            job_id=ctx.job.id,
            severity=Severity.info,
            category=FindingCategory.static,
            title=f"Static analysis: {fmt.upper()} binary",
            description=f"SHA256: {sha256[:16]}..., Size: {size}, Entropy: {entropy:.2f}",
            evidence=[Evidence(type="pattern", value=f"format={fmt}")],
            confidence=1.0,
            tags=["static", fmt]
        ))

        exec_time = int((time.time() - start) * 1000)

        return PluginResult(
            findings=findings,
            artifacts=artifacts,
            events=events,
            success=True,
            execution_time_ms=exec_time,
            context_data={
                "sha256": sha256,
                "format": fmt,
                "entropy": entropy,
                "strings_count": len(strings)
            }
        )
