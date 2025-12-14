"""Valkyrie — Binary Diff and Evolution Tracker.

Valkyrie performs semantic binary diffing to:
- Identify changed functions between versions
- Score risk of code changes
- Track binary evolution over time
- Generate visual diff heatmaps

Unlike raw byte diffing, Valkyrie operates at the function/block level
to provide meaningful security-relevant insights.
"""

from __future__ import annotations
import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

from aetherframe.plugins.base import Plugin, PluginManifest, PluginValidationError
from aetherframe.schemas import (
    JobContext, PluginResult,
    Finding, Severity, FindingCategory, Evidence,
    Artifact, ArtifactType,
    TraceEvent, EventSource, EventType
)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ChangeType(str, Enum):
    """Types of binary changes."""
    added = "added"
    removed = "removed"
    modified = "modified"
    unchanged = "unchanged"


@dataclass
class Function:
    """Represents a function extracted from a binary."""
    name: str
    address: int
    size: int
    hash: str  # Content hash for quick comparison
    instructions: int = 0
    calls: List[str] = field(default_factory=list)
    strings: List[str] = field(default_factory=list)
    is_import: bool = False
    is_export: bool = False
    complexity: int = 0  # Cyclomatic complexity estimate

    def signature_hash(self) -> str:
        """Generate a signature hash based on structure, not addresses."""
        sig = f"{self.size}:{self.instructions}:{len(self.calls)}:{self.complexity}"
        return hashlib.md5(sig.encode()).hexdigest()[:16]


@dataclass
class FunctionDiff:
    """Difference between two function versions."""
    name: str
    change_type: ChangeType
    old_function: Optional[Function] = None
    new_function: Optional[Function] = None
    size_delta: int = 0
    instruction_delta: int = 0
    call_changes: List[str] = field(default_factory=list)
    string_changes: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    risk_reasons: List[str] = field(default_factory=list)


@dataclass
class BinaryMetadata:
    """Metadata extracted from a binary."""
    path: str
    sha256: str
    size: int
    format: str  # pe, elf, macho
    arch: str  # x86, x64, arm, arm64
    functions: List[Function] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    strings: List[str] = field(default_factory=list)


@dataclass
class DiffResult:
    """Complete diff result between two binaries."""
    old_binary: BinaryMetadata
    new_binary: BinaryMetadata
    function_diffs: List[FunctionDiff] = field(default_factory=list)
    added_imports: List[str] = field(default_factory=list)
    removed_imports: List[str] = field(default_factory=list)
    added_exports: List[str] = field(default_factory=list)
    removed_exports: List[str] = field(default_factory=list)
    overall_risk: float = 0.0
    summary: Dict[str, int] = field(default_factory=dict)


# ============================================================================
# RISK SCORING
# ============================================================================

# Suspicious API patterns that increase risk score
HIGH_RISK_APIS = {
    # Process manipulation
    "CreateRemoteThread": 0.9,
    "VirtualAllocEx": 0.8,
    "WriteProcessMemory": 0.9,
    "NtUnmapViewOfSection": 0.9,
    "SetThreadContext": 0.8,
    # Code injection
    "LoadLibrary": 0.5,
    "GetProcAddress": 0.4,
    # Privilege escalation
    "AdjustTokenPrivileges": 0.7,
    "OpenProcessToken": 0.6,
    # Persistence
    "RegSetValueEx": 0.5,
    "CreateService": 0.7,
    # Network
    "WSAStartup": 0.4,
    "connect": 0.4,
    "send": 0.3,
    "recv": 0.3,
    # Crypto
    "CryptEncrypt": 0.6,
    "CryptDecrypt": 0.6,
    # File system
    "DeleteFile": 0.4,
    "MoveFile": 0.3,
}

# Suspicious strings that increase risk
HIGH_RISK_STRINGS = {
    "cmd.exe": 0.5,
    "powershell": 0.6,
    "/bin/sh": 0.5,
    "password": 0.3,
    "encrypt": 0.4,
    "decrypt": 0.4,
    "ransom": 0.9,
    "bitcoin": 0.6,
    ".onion": 0.7,
}


def calculate_function_risk(diff: FunctionDiff) -> Tuple[float, List[str]]:
    """Calculate risk score for a function change."""
    risk = 0.0
    reasons = []

    if diff.change_type == ChangeType.added:
        # New functions are inherently suspicious
        risk += 0.3
        reasons.append("New function added")

        # Check for suspicious calls
        if diff.new_function:
            for call in diff.new_function.calls:
                call_base = call.split("!")[-1] if "!" in call else call
                if call_base in HIGH_RISK_APIS:
                    api_risk = HIGH_RISK_APIS[call_base]
                    risk += api_risk * 0.5  # Weighted
                    reasons.append(f"Suspicious API: {call_base}")

            # Check strings
            for s in diff.new_function.strings:
                for pattern, pattern_risk in HIGH_RISK_STRINGS.items():
                    if pattern.lower() in s.lower():
                        risk += pattern_risk * 0.3
                        reasons.append(f"Suspicious string: {pattern}")
                        break

    elif diff.change_type == ChangeType.modified:
        risk += 0.2
        reasons.append("Function modified")

        # Size increase is suspicious
        if diff.size_delta > 100:
            risk += 0.2
            reasons.append(f"Size increased by {diff.size_delta} bytes")

        # Instruction increase
        if diff.instruction_delta > 20:
            risk += 0.15
            reasons.append(f"Instructions increased by {diff.instruction_delta}")

        # New calls added
        for call in diff.call_changes:
            if call.startswith("+"):
                call_name = call[1:].split("!")[-1] if "!" in call else call[1:]
                if call_name in HIGH_RISK_APIS:
                    risk += HIGH_RISK_APIS[call_name] * 0.4
                    reasons.append(f"New suspicious call: {call_name}")

    elif diff.change_type == ChangeType.removed:
        # Removed functions are less suspicious but worth noting
        risk += 0.1
        reasons.append("Function removed")

    return min(risk, 1.0), reasons


# ============================================================================
# BINARY ANALYSIS
# ============================================================================

def analyze_binary(path: Path) -> BinaryMetadata:
    """Extract metadata and functions from a binary.

    This is a simplified implementation. In production, this would use:
    - LIEF for PE/ELF/Mach-O parsing
    - Capstone for disassembly
    - angr/Binary Ninja for CFG analysis
    """
    data = path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()

    # Detect format
    format_type = "unknown"
    arch = "unknown"

    if data[:2] == b"MZ":
        format_type = "pe"
        # Check for PE32 vs PE32+
        if len(data) > 0x3C + 4:
            pe_offset = int.from_bytes(data[0x3C:0x3C+4], "little")
            if len(data) > pe_offset + 6:
                machine = int.from_bytes(data[pe_offset+4:pe_offset+6], "little")
                arch = "x64" if machine == 0x8664 else "x86"
    elif data[:4] == b"\x7fELF":
        format_type = "elf"
        arch = "x64" if data[4] == 2 else "x86"
    elif data[:4] in (b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf",
                       b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe"):
        format_type = "macho"
        arch = "x64" if data[4] in (0xcf, 0x07) else "x86"

    # Extract printable strings (simplified)
    strings = extract_strings(data, min_length=6)

    # Simulate function extraction (simplified heuristic)
    # In production, use proper disassembly
    functions = extract_functions_heuristic(data, format_type)

    # Simulate import extraction
    imports = []
    if format_type == "pe":
        imports = extract_pe_imports_heuristic(data)

    return BinaryMetadata(
        path=str(path),
        sha256=sha256,
        size=len(data),
        format=format_type,
        arch=arch,
        functions=functions,
        imports=imports,
        exports=[],
        sections=[],
        strings=strings[:500]  # Limit
    )


def extract_strings(data: bytes, min_length: int = 4) -> List[str]:
    """Extract printable ASCII strings from binary data."""
    import re
    pattern = rb"[\x20-\x7e]{" + str(min_length).encode() + rb",}"
    matches = re.findall(pattern, data)
    return [m.decode("ascii", errors="ignore") for m in matches[:1000]]


def extract_functions_heuristic(data: bytes, format_type: str) -> List[Function]:
    """Extract functions using heuristics (simplified).

    In production, use:
    - radare2/rizin
    - Binary Ninja
    - angr/CFG recovery
    """
    functions = []

    # Look for common function prologs
    if format_type in ("pe", "elf"):
        # x86/x64 function prologs
        prologs = [
            b"\x55\x8B\xEC",  # push ebp; mov ebp, esp
            b"\x55\x48\x89\xE5",  # push rbp; mov rbp, rsp
            b"\x55\x89\xE5",  # push ebp; mov ebp, esp (32-bit)
        ]

        for prolog in prologs:
            offset = 0
            while True:
                pos = data.find(prolog, offset)
                if pos == -1:
                    break

                # Estimate function size (look for ret)
                func_end = data.find(b"\xC3", pos + len(prolog))
                if func_end == -1:
                    func_end = pos + 100

                size = min(func_end - pos + 1, 4096)  # Cap at 4KB
                func_data = data[pos:pos + size]

                functions.append(Function(
                    name=f"sub_{pos:08x}",
                    address=pos,
                    size=size,
                    hash=hashlib.md5(func_data).hexdigest(),
                    instructions=size // 4,  # Rough estimate
                    complexity=count_branches(func_data)
                ))

                offset = pos + 1

                if len(functions) >= 500:  # Limit
                    break

            if len(functions) >= 500:
                break

    return functions


def count_branches(data: bytes) -> int:
    """Count branch instructions (simplified complexity metric)."""
    branches = 0
    # x86/x64 conditional jumps
    for opcode in [0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D, 0x7E, 0x7F]:
        branches += data.count(bytes([opcode]))
    # Near jumps
    branches += data.count(b"\x0F\x84")
    branches += data.count(b"\x0F\x85")
    return branches


def extract_pe_imports_heuristic(data: bytes) -> List[str]:
    """Extract import names from PE (simplified)."""
    imports = []

    # Look for common DLL names and their imports
    common_dlls = [b"kernel32.dll", b"user32.dll", b"ntdll.dll", b"advapi32.dll"]

    for dll in common_dlls:
        if dll in data.lower():
            imports.append(dll.decode())

    # Look for API names
    for api in HIGH_RISK_APIS.keys():
        if api.encode() in data:
            imports.append(api)

    return imports


# ============================================================================
# DIFFING ENGINE
# ============================================================================

def diff_binaries(old: BinaryMetadata, new: BinaryMetadata, semantic: bool = True) -> DiffResult:
    """Compute diff between two binaries."""
    result = DiffResult(old_binary=old, new_binary=new)

    # Match functions
    old_funcs = {f.name: f for f in old.functions}
    new_funcs = {f.name: f for f in new.functions}

    old_names = set(old_funcs.keys())
    new_names = set(new_funcs.keys())

    # Simple name-based matching first
    added = new_names - old_names
    removed = old_names - new_names
    common = old_names & new_names

    # Process removed functions
    for name in removed:
        func = old_funcs[name]
        diff = FunctionDiff(
            name=name,
            change_type=ChangeType.removed,
            old_function=func
        )
        diff.risk_score, diff.risk_reasons = calculate_function_risk(diff)
        result.function_diffs.append(diff)

    # Process added functions
    for name in added:
        func = new_funcs[name]
        diff = FunctionDiff(
            name=name,
            change_type=ChangeType.added,
            new_function=func
        )
        diff.risk_score, diff.risk_reasons = calculate_function_risk(diff)
        result.function_diffs.append(diff)

    # Process common functions
    for name in common:
        old_func = old_funcs[name]
        new_func = new_funcs[name]

        if semantic:
            # Compare by signature hash (ignores addresses)
            changed = old_func.signature_hash() != new_func.signature_hash()
        else:
            # Compare by content hash
            changed = old_func.hash != new_func.hash

        if changed:
            diff = FunctionDiff(
                name=name,
                change_type=ChangeType.modified,
                old_function=old_func,
                new_function=new_func,
                size_delta=new_func.size - old_func.size,
                instruction_delta=new_func.instructions - old_func.instructions
            )

            # Compute call changes
            old_calls = set(old_func.calls)
            new_calls = set(new_func.calls)
            diff.call_changes = [f"+{c}" for c in (new_calls - old_calls)]
            diff.call_changes += [f"-{c}" for c in (old_calls - new_calls)]

            diff.risk_score, diff.risk_reasons = calculate_function_risk(diff)
            result.function_diffs.append(diff)

    # Import/export changes
    old_imports = set(old.imports)
    new_imports = set(new.imports)
    result.added_imports = list(new_imports - old_imports)
    result.removed_imports = list(old_imports - new_imports)

    # Calculate overall risk
    if result.function_diffs:
        result.overall_risk = sum(d.risk_score for d in result.function_diffs) / len(result.function_diffs)
        # Boost for added imports
        for imp in result.added_imports:
            if imp in HIGH_RISK_APIS:
                result.overall_risk = min(result.overall_risk + 0.1, 1.0)

    # Summary
    result.summary = {
        "added": len([d for d in result.function_diffs if d.change_type == ChangeType.added]),
        "removed": len([d for d in result.function_diffs if d.change_type == ChangeType.removed]),
        "modified": len([d for d in result.function_diffs if d.change_type == ChangeType.modified]),
        "total_changes": len(result.function_diffs),
        "added_imports": len(result.added_imports),
        "removed_imports": len(result.removed_imports)
    }

    return result


# ============================================================================
# VALKYRIE PLUGIN
# ============================================================================

class ValkyriePlugin(Plugin):
    """Valkyrie Binary Diff Plugin.

    Compares binaries and identifies security-relevant changes.
    Used in release-watch pipelines to track malware evolution
    or detect patches that introduce vulnerabilities.
    """

    def validate(self, ctx: JobContext) -> None:
        """Validate inputs for diffing."""
        target = Path(ctx.target_path)

        if not target.exists():
            raise PluginValidationError(self.id, f"Target file not found: {target}")

        # For diff mode, we need a reference
        # This can come from:
        # 1. Job options (explicit reference file)
        # 2. Previous artifacts (from pipeline context)
        # 3. Database lookup (by hash/name)

        # For now, require explicit reference in options
        if "reference_path" not in ctx.job.options and "reference_job_id" not in ctx.job.options:
            # Allow single-file mode for metadata extraction
            pass

    def run(self, ctx: JobContext) -> PluginResult:
        """Execute binary diff or analysis."""
        import time
        start_time = time.time()

        target = Path(ctx.target_path)
        findings: List[Finding] = []
        artifacts: List[Artifact] = []
        events: List[TraceEvent] = []

        semantic = self.config.get("semantic", True)
        generate_heatmap = self.config.get("generate_heatmap", True)
        compute_risk = self.config.get("compute_risk", True)

        # Emit start event
        events.append(TraceEvent(
            job_id=ctx.job.id,
            source=EventSource.valkyrie,
            event_type=EventType.info,
            payload={"action": "diff_start", "target": str(target)}
        ))

        # Analyze current binary
        new_meta = analyze_binary(target)

        # Check for reference
        reference_path = ctx.job.options.get("reference_path")

        if reference_path:
            ref_path = Path(reference_path)
            if not ref_path.exists():
                raise PluginValidationError(self.id, f"Reference file not found: {ref_path}")

            old_meta = analyze_binary(ref_path)

            # Perform diff
            diff_result = diff_binaries(old_meta, new_meta, semantic=semantic)

            # Generate findings from diff
            findings.extend(self._generate_diff_findings(ctx, diff_result))

            # Generate artifacts
            artifacts.extend(self._generate_diff_artifacts(ctx, diff_result, generate_heatmap))

            risk_score = diff_result.overall_risk
            context_data = {
                "diff_summary": diff_result.summary,
                "overall_risk": diff_result.overall_risk,
                "has_high_risk_changes": any(d.risk_score >= 0.7 for d in diff_result.function_diffs)
            }
        else:
            # Single file mode - just extract metadata
            artifacts.append(self._generate_metadata_artifact(ctx, new_meta))
            risk_score = 0.0
            context_data = {
                "binary_metadata": {
                    "sha256": new_meta.sha256,
                    "format": new_meta.format,
                    "arch": new_meta.arch,
                    "functions": len(new_meta.functions),
                    "imports": len(new_meta.imports)
                }
            }

        execution_time = int((time.time() - start_time) * 1000)

        return PluginResult(
            findings=findings,
            artifacts=artifacts,
            events=events,
            success=True,
            execution_time_ms=execution_time,
            risk_score=risk_score,
            context_data=context_data
        )

    def _generate_diff_findings(self, ctx: JobContext, diff: DiffResult) -> List[Finding]:
        """Generate findings from diff result."""
        findings = []

        # High-risk function changes
        for func_diff in diff.function_diffs:
            if func_diff.risk_score >= 0.5:
                severity = Severity.critical if func_diff.risk_score >= 0.8 else \
                          Severity.high if func_diff.risk_score >= 0.6 else Severity.medium

                category = {
                    ChangeType.added: FindingCategory.new_code,
                    ChangeType.removed: FindingCategory.removed_code,
                    ChangeType.modified: FindingCategory.function_change
                }.get(func_diff.change_type, FindingCategory.binary_diff)

                findings.append(Finding(
                    job_id=ctx.job.id,
                    severity=severity,
                    category=category,
                    title=f"High-risk {func_diff.change_type.value}: {func_diff.name}",
                    description="; ".join(func_diff.risk_reasons),
                    evidence=[
                        Evidence(
                            type="function",
                            location=f"0x{func_diff.new_function.address:08x}" if func_diff.new_function else "N/A",
                            value=f"size_delta={func_diff.size_delta}, risk={func_diff.risk_score:.2f}",
                            context=f"Change type: {func_diff.change_type.value}"
                        )
                    ],
                    confidence=0.85,
                    tags=["valkyrie", func_diff.change_type.value]
                ))

        # Import changes
        for imp in diff.added_imports:
            if imp in HIGH_RISK_APIS:
                findings.append(Finding(
                    job_id=ctx.job.id,
                    severity=Severity.high,
                    category=FindingCategory.binary_diff,
                    title=f"New suspicious import: {imp}",
                    description=f"Newly added import {imp} is associated with malicious behavior",
                    evidence=[Evidence(type="string", value=imp)],
                    confidence=HIGH_RISK_APIS[imp],
                    tags=["valkyrie", "import", "new"]
                ))

        # Summary finding
        if diff.function_diffs:
            findings.append(Finding(
                job_id=ctx.job.id,
                severity=Severity.info,
                category=FindingCategory.binary_diff,
                title=f"Binary diff summary: {diff.summary['total_changes']} changes",
                description=f"Added: {diff.summary['added']}, Removed: {diff.summary['removed']}, Modified: {diff.summary['modified']}",
                evidence=[Evidence(
                    type="pattern",
                    value=json.dumps(diff.summary)
                )],
                confidence=1.0,
                tags=["valkyrie", "summary"]
            ))

        return findings

    def _generate_diff_artifacts(
        self,
        ctx: JobContext,
        diff: DiffResult,
        generate_heatmap: bool
    ) -> List[Artifact]:
        """Generate artifacts from diff result."""
        artifacts = []

        # Full diff report
        report = {
            "plugin": "valkyrie",
            "version": self.version,
            "old_binary": {
                "path": diff.old_binary.path,
                "sha256": diff.old_binary.sha256,
                "size": diff.old_binary.size,
                "format": diff.old_binary.format,
                "functions": len(diff.old_binary.functions)
            },
            "new_binary": {
                "path": diff.new_binary.path,
                "sha256": diff.new_binary.sha256,
                "size": diff.new_binary.size,
                "format": diff.new_binary.format,
                "functions": len(diff.new_binary.functions)
            },
            "summary": diff.summary,
            "overall_risk": diff.overall_risk,
            "function_diffs": [
                {
                    "name": d.name,
                    "change_type": d.change_type.value,
                    "size_delta": d.size_delta,
                    "instruction_delta": d.instruction_delta,
                    "risk_score": d.risk_score,
                    "risk_reasons": d.risk_reasons
                }
                for d in diff.function_diffs
            ],
            "added_imports": diff.added_imports,
            "removed_imports": diff.removed_imports
        }

        report_path = ctx.get_artifact_path("diff_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        artifacts.append(Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.diff,
            name="diff_report.json",
            description="Valkyrie binary diff report",
            uri=f"file://{report_path}",
            meta={"changes": diff.summary["total_changes"], "risk": diff.overall_risk}
        ))

        # Heatmap data
        if generate_heatmap and diff.function_diffs:
            heatmap = self._generate_heatmap_data(diff)
            heatmap_path = ctx.get_artifact_path("diff_heatmap.json")
            with open(heatmap_path, "w") as f:
                json.dump(heatmap, f, indent=2)

            artifacts.append(Artifact(
                job_id=ctx.job.id,
                artifact_type=ArtifactType.heatmap,
                name="diff_heatmap.json",
                description="Visual diff heatmap data",
                uri=f"file://{heatmap_path}",
                meta={"cells": len(heatmap["cells"])}
            ))

        return artifacts

    def _generate_heatmap_data(self, diff: DiffResult) -> Dict[str, Any]:
        """Generate heatmap visualization data."""
        cells = []

        for func_diff in diff.function_diffs:
            addr = func_diff.new_function.address if func_diff.new_function else \
                   func_diff.old_function.address if func_diff.old_function else 0
            size = func_diff.new_function.size if func_diff.new_function else \
                   func_diff.old_function.size if func_diff.old_function else 0

            cells.append({
                "name": func_diff.name,
                "address": addr,
                "size": size,
                "change_type": func_diff.change_type.value,
                "risk": func_diff.risk_score,
                "color": self._risk_to_color(func_diff.risk_score, func_diff.change_type)
            })

        return {
            "title": "Binary Diff Heatmap",
            "cells": sorted(cells, key=lambda x: x["address"]),
            "legend": {
                "added": "#22c55e",
                "removed": "#ef4444",
                "modified_low": "#fbbf24",
                "modified_high": "#f97316"
            }
        }

    def _risk_to_color(self, risk: float, change_type: ChangeType) -> str:
        """Convert risk score and change type to color."""
        if change_type == ChangeType.added:
            return "#22c55e" if risk < 0.5 else "#16a34a"
        elif change_type == ChangeType.removed:
            return "#ef4444"
        else:
            if risk < 0.3:
                return "#fbbf24"
            elif risk < 0.6:
                return "#f97316"
            else:
                return "#ef4444"

    def _generate_metadata_artifact(self, ctx: JobContext, meta: BinaryMetadata) -> Artifact:
        """Generate metadata artifact for single file mode."""
        data = {
            "path": meta.path,
            "sha256": meta.sha256,
            "size": meta.size,
            "format": meta.format,
            "arch": meta.arch,
            "functions": len(meta.functions),
            "imports": meta.imports,
            "exports": meta.exports
        }

        path = ctx.get_artifact_path("binary_metadata.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.json,
            name="binary_metadata.json",
            description="Binary metadata extraction",
            uri=f"file://{path}"
        )
