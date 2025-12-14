"""Umbriel — Anti-Analysis Detection Engine.

Umbriel is the gate guardian of AetherFrame. It runs FIRST in pipelines
to detect evasion techniques that might affect subsequent analysis.

Detection categories:
- Anti-Debug: IsDebuggerPresent, NtQueryInformationProcess, timing checks
- Anti-VM: CPUID checks, registry queries, hardware fingerprinting
- Anti-Frida: Frida-specific strings, module detection patterns
- Packing: Entropy analysis, section anomalies, known packers
- Timing: RDTSC abuse, GetTickCount patterns
"""

from __future__ import annotations
import hashlib
import math
import re
import struct
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from aetherframe.plugins.base import Plugin, PluginManifest, PluginValidationError
from aetherframe.schemas import (
    JobContext, PluginResult,
    Finding, FindingCreate, Severity, FindingCategory, Evidence,
    Artifact, ArtifactType,
    TraceEvent, EventSource, EventType
)


# ============================================================================
# DETECTION SIGNATURES
# ============================================================================

@dataclass
class DetectionSignature:
    """A detection signature for anti-analysis techniques."""
    id: str
    name: str
    category: FindingCategory
    severity: Severity
    pattern: bytes  # Byte pattern to match
    mask: Optional[bytes] = None  # Optional mask for wildcard matching
    description: str = ""
    confidence: float = 0.9
    tags: List[str] = field(default_factory=list)


# Windows Anti-Debug APIs
ANTI_DEBUG_SIGNATURES = [
    DetectionSignature(
        id="AD001",
        name="IsDebuggerPresent",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"IsDebuggerPresent",
        description="Direct debugger detection via kernel32 API",
        tags=["windows", "kernel32", "direct"]
    ),
    DetectionSignature(
        id="AD002",
        name="CheckRemoteDebuggerPresent",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"CheckRemoteDebuggerPresent",
        description="Remote debugger detection",
        tags=["windows", "kernel32", "remote"]
    ),
    DetectionSignature(
        id="AD003",
        name="NtQueryInformationProcess",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"NtQueryInformationProcess",
        description="Low-level process query for debug flags",
        tags=["windows", "ntdll", "native"]
    ),
    DetectionSignature(
        id="AD004",
        name="NtSetInformationThread",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"NtSetInformationThread",
        description="Thread hiding from debugger (HideFromDebugger)",
        tags=["windows", "ntdll", "thread"]
    ),
    DetectionSignature(
        id="AD005",
        name="OutputDebugString",
        category=FindingCategory.anti_debug,
        severity=Severity.medium,
        pattern=b"OutputDebugStringA",
        description="Debug string trap (checks for attached debugger)",
        tags=["windows", "kernel32"]
    ),
    DetectionSignature(
        id="AD006",
        name="DebugActiveProcess",
        category=FindingCategory.anti_debug,
        severity=Severity.medium,
        pattern=b"DebugActiveProcess",
        description="Self-debugging technique",
        tags=["windows", "kernel32", "self-debug"]
    ),
    DetectionSignature(
        id="AD007",
        name="INT 3 Breakpoint",
        category=FindingCategory.anti_debug,
        severity=Severity.medium,
        pattern=b"\xCC",  # INT 3
        description="Software breakpoint detection",
        confidence=0.6,
        tags=["x86", "breakpoint"]
    ),
    DetectionSignature(
        id="AD008",
        name="INT 2D",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"\xCD\x2D",  # INT 2D
        description="Kernel debugger detection interrupt",
        tags=["x86", "kernel-debug"]
    ),
    # Linux ptrace
    DetectionSignature(
        id="AD009",
        name="ptrace PTRACE_TRACEME",
        category=FindingCategory.anti_debug,
        severity=Severity.high,
        pattern=b"ptrace",
        description="Linux anti-debug via ptrace self-attach",
        tags=["linux", "ptrace"]
    ),
]

# Anti-VM Signatures
ANTI_VM_SIGNATURES = [
    DetectionSignature(
        id="VM001",
        name="VMware Detection",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"VMware",
        description="VMware hypervisor string check",
        tags=["vmware", "string"]
    ),
    DetectionSignature(
        id="VM002",
        name="VirtualBox Detection",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"VirtualBox",
        description="VirtualBox hypervisor string check",
        tags=["virtualbox", "string"]
    ),
    DetectionSignature(
        id="VM003",
        name="VBox Guest Additions",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"VBoxGuest",
        description="VirtualBox Guest Additions detection",
        tags=["virtualbox", "driver"]
    ),
    DetectionSignature(
        id="VM004",
        name="QEMU Detection",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"QEMU",
        description="QEMU emulator string check",
        tags=["qemu", "string"]
    ),
    DetectionSignature(
        id="VM005",
        name="Hyper-V Detection",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"Hyper-V",
        description="Microsoft Hyper-V detection",
        tags=["hyperv", "microsoft"]
    ),
    DetectionSignature(
        id="VM006",
        name="Xen Detection",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"Xen",
        description="Xen hypervisor detection",
        tags=["xen", "string"]
    ),
    DetectionSignature(
        id="VM007",
        name="CPUID Hypervisor Bit",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"\x0F\xA2",  # CPUID instruction
        description="CPUID instruction (may check hypervisor bit)",
        confidence=0.7,
        tags=["cpuid", "x86"]
    ),
    DetectionSignature(
        id="VM008",
        name="VMware I/O Port",
        category=FindingCategory.anti_vm,
        severity=Severity.critical,
        pattern=b"VMXh",
        description="VMware magic I/O port backdoor",
        tags=["vmware", "backdoor"]
    ),
    DetectionSignature(
        id="VM009",
        name="SIDT/SGDT Red Pill",
        category=FindingCategory.anti_vm,
        severity=Severity.high,
        pattern=b"\x0F\x01",  # SIDT/SGDT prefix
        description="Red Pill technique (SIDT/SGDT relocation)",
        confidence=0.6,
        tags=["redpill", "x86"]
    ),
    # Registry checks
    DetectionSignature(
        id="VM010",
        name="VM Registry Key",
        category=FindingCategory.anti_vm,
        severity=Severity.medium,
        pattern=b"SYSTEM\\CurrentControlSet\\Services\\Disk\\Enum",
        description="Disk enumeration registry check",
        tags=["windows", "registry"]
    ),
]

# Anti-Frida Signatures
ANTI_FRIDA_SIGNATURES = [
    DetectionSignature(
        id="FR001",
        name="Frida Library Name",
        category=FindingCategory.anti_frida,
        severity=Severity.critical,
        pattern=b"frida-agent",
        description="Frida agent library name detection",
        tags=["frida", "library"]
    ),
    DetectionSignature(
        id="FR002",
        name="Frida RPC",
        category=FindingCategory.anti_frida,
        severity=Severity.high,
        pattern=b"frida:rpc",
        description="Frida RPC protocol string",
        tags=["frida", "rpc"]
    ),
    DetectionSignature(
        id="FR003",
        name="Frida Gadget",
        category=FindingCategory.anti_frida,
        severity=Severity.critical,
        pattern=b"FridaGadget",
        description="Frida Gadget injection marker",
        tags=["frida", "gadget"]
    ),
    DetectionSignature(
        id="FR004",
        name="Frida Server Port",
        category=FindingCategory.anti_frida,
        severity=Severity.high,
        pattern=b"27042",  # Default Frida port
        description="Default Frida server port",
        confidence=0.7,
        tags=["frida", "port"]
    ),
    DetectionSignature(
        id="FR005",
        name="Frida Thread Name",
        category=FindingCategory.anti_frida,
        severity=Severity.high,
        pattern=b"gum-js-loop",
        description="Frida GumJS thread name",
        tags=["frida", "thread"]
    ),
    DetectionSignature(
        id="FR006",
        name="Frida Maps Check",
        category=FindingCategory.anti_frida,
        severity=Severity.high,
        pattern=b"/proc/self/maps",
        description="Process maps enumeration (Frida detection)",
        confidence=0.6,
        tags=["linux", "android", "maps"]
    ),
]

# Timing check patterns
TIMING_SIGNATURES = [
    DetectionSignature(
        id="TM001",
        name="RDTSC Instruction",
        category=FindingCategory.timing_check,
        severity=Severity.medium,
        pattern=b"\x0F\x31",  # RDTSC
        description="RDTSC timing check",
        confidence=0.7,
        tags=["x86", "rdtsc"]
    ),
    DetectionSignature(
        id="TM002",
        name="GetTickCount",
        category=FindingCategory.timing_check,
        severity=Severity.medium,
        pattern=b"GetTickCount",
        description="Windows timing via GetTickCount",
        tags=["windows", "kernel32"]
    ),
    DetectionSignature(
        id="TM003",
        name="QueryPerformanceCounter",
        category=FindingCategory.timing_check,
        severity=Severity.medium,
        pattern=b"QueryPerformanceCounter",
        description="High-resolution timing check",
        tags=["windows", "kernel32"]
    ),
    DetectionSignature(
        id="TM004",
        name="clock_gettime",
        category=FindingCategory.timing_check,
        severity=Severity.medium,
        pattern=b"clock_gettime",
        description="Linux high-resolution timing",
        tags=["linux", "libc"]
    ),
]

# Packer signatures
PACKER_SIGNATURES = [
    DetectionSignature(
        id="PK001",
        name="UPX Packer",
        category=FindingCategory.packing,
        severity=Severity.medium,
        pattern=b"UPX!",
        description="UPX packer signature",
        tags=["upx", "packer"]
    ),
    DetectionSignature(
        id="PK002",
        name="UPX Section",
        category=FindingCategory.packing,
        severity=Severity.medium,
        pattern=b"UPX0",
        description="UPX section header",
        tags=["upx", "section"]
    ),
    DetectionSignature(
        id="PK003",
        name="ASPack",
        category=FindingCategory.packing,
        severity=Severity.medium,
        pattern=b"ASPack",
        description="ASPack packer",
        tags=["aspack", "packer"]
    ),
    DetectionSignature(
        id="PK004",
        name="Themida",
        category=FindingCategory.packing,
        severity=Severity.high,
        pattern=b"Themida",
        description="Themida protector/packer",
        tags=["themida", "protector"]
    ),
    DetectionSignature(
        id="PK005",
        name="VMProtect",
        category=FindingCategory.packing,
        severity=Severity.high,
        pattern=b".vmp",
        description="VMProtect section",
        tags=["vmprotect", "protector"]
    ),
    DetectionSignature(
        id="PK006",
        name="Enigma Protector",
        category=FindingCategory.packing,
        severity=Severity.high,
        pattern=b"Enigma",
        description="Enigma Protector",
        tags=["enigma", "protector"]
    ),
]

ALL_SIGNATURES = (
    ANTI_DEBUG_SIGNATURES +
    ANTI_VM_SIGNATURES +
    ANTI_FRIDA_SIGNATURES +
    TIMING_SIGNATURES +
    PACKER_SIGNATURES
)


# ============================================================================
# ENTROPY ANALYSIS
# ============================================================================

def calculate_entropy(data: bytes) -> float:
    """Calculate Shannon entropy of data."""
    if not data:
        return 0.0

    counter = Counter(data)
    length = len(data)
    entropy = 0.0

    for count in counter.values():
        if count > 0:
            probability = count / length
            entropy -= probability * math.log2(probability)

    return entropy


def analyze_entropy_sections(data: bytes, chunk_size: int = 4096) -> List[Dict[str, Any]]:
    """Analyze entropy across sections of the binary."""
    sections = []
    offset = 0

    while offset < len(data):
        chunk = data[offset:offset + chunk_size]
        entropy = calculate_entropy(chunk)
        sections.append({
            "offset": offset,
            "size": len(chunk),
            "entropy": round(entropy, 4)
        })
        offset += chunk_size

    return sections


# ============================================================================
# UMBRIEL PLUGIN
# ============================================================================

class UmbrielPlugin(Plugin):
    """Umbriel Anti-Analysis Detection Plugin.

    Runs as a GATE at the start of pipelines to detect techniques
    that might interfere with subsequent analysis stages.
    """

    def validate(self, ctx: JobContext) -> None:
        """Validate that we can analyze the target."""
        target = Path(ctx.target_path)

        if not target.exists():
            raise PluginValidationError(self.id, f"Target file not found: {target}")

        if not target.is_file():
            raise PluginValidationError(self.id, f"Target is not a file: {target}")

        # Check file size (limit to 100MB for now)
        if target.stat().st_size > 100 * 1024 * 1024:
            raise PluginValidationError(self.id, "Target file too large (>100MB)")

    def run(self, ctx: JobContext) -> PluginResult:
        """Execute anti-analysis detection."""
        import time
        start_time = time.time()

        target = Path(ctx.target_path)
        data = target.read_bytes()

        findings: List[Finding] = []
        events: List[TraceEvent] = []

        mode = self.config.get("mode", "thorough")
        skip_entropy = self.config.get("skip_entropy", False)
        entropy_threshold = self.config.get("entropy_threshold", 7.0)
        skip_vm = self.config.get("skip_vm_checks", False)
        skip_frida = self.config.get("skip_frida_checks", False)

        # Emit start event
        events.append(TraceEvent(
            job_id=ctx.job.id,
            source=EventSource.umbriel,
            event_type=EventType.info,
            payload={"action": "scan_start", "target": str(target), "mode": mode}
        ))

        # Select signatures based on config
        signatures = ANTI_DEBUG_SIGNATURES + TIMING_SIGNATURES + PACKER_SIGNATURES
        if not skip_vm:
            signatures += ANTI_VM_SIGNATURES
        if not skip_frida:
            signatures += ANTI_FRIDA_SIGNATURES

        # Run signature detection
        for sig in signatures:
            matches = self._find_pattern(data, sig.pattern, sig.mask)
            for offset in matches:
                finding = Finding(
                    job_id=ctx.job.id,
                    severity=sig.severity,
                    category=sig.category,
                    title=f"{sig.name} detected",
                    description=sig.description,
                    evidence=[Evidence(
                        type="bytes",
                        location=f"0x{offset:08x}",
                        value=sig.pattern.hex() if len(sig.pattern) < 32 else sig.pattern[:32].hex() + "...",
                        context=f"Signature ID: {sig.id}"
                    )],
                    confidence=sig.confidence,
                    tags=sig.tags + [sig.id]
                )
                findings.append(finding)

        # Entropy analysis
        entropy_findings = []
        overall_entropy = 0.0
        if not skip_entropy:
            overall_entropy = calculate_entropy(data)
            if overall_entropy >= entropy_threshold:
                entropy_findings.append(Finding(
                    job_id=ctx.job.id,
                    severity=Severity.high,
                    category=FindingCategory.packing,
                    title="High entropy detected",
                    description=f"Overall entropy {overall_entropy:.2f} >= {entropy_threshold} suggests packing/encryption",
                    evidence=[Evidence(
                        type="pattern",
                        value=f"entropy={overall_entropy:.4f}",
                        context="Shannon entropy of entire file"
                    )],
                    confidence=0.85,
                    tags=["entropy", "packing"]
                ))
            findings.extend(entropy_findings)

        # Section entropy analysis (thorough mode only)
        section_entropies = []
        if mode == "thorough" and not skip_entropy:
            section_entropies = analyze_entropy_sections(data)
            high_entropy_sections = [s for s in section_entropies if s["entropy"] >= entropy_threshold]
            if high_entropy_sections:
                for section in high_entropy_sections[:5]:  # Limit to 5
                    findings.append(Finding(
                        job_id=ctx.job.id,
                        severity=Severity.medium,
                        category=FindingCategory.packing,
                        title=f"High entropy section at 0x{section['offset']:x}",
                        description=f"Section entropy {section['entropy']:.2f} suggests encrypted/packed data",
                        evidence=[Evidence(
                            type="bytes",
                            location=f"0x{section['offset']:08x}",
                            value=f"size={section['size']}, entropy={section['entropy']:.4f}"
                        )],
                        confidence=0.75,
                        tags=["entropy", "section"]
                    ))

        # Calculate risk score
        risk_score = self._calculate_risk_score(findings)

        # Generate artifacts
        artifacts = self._generate_artifacts(ctx, findings, overall_entropy, section_entropies)

        # Recommendations
        recommendations = []
        if risk_score >= 0.7:
            recommendations.append("Consider dynamic analysis with LainTrace due to high evasion risk")
        if any(f.category == FindingCategory.packing for f in findings):
            recommendations.append("Unpack binary before static analysis")
        if any(f.category == FindingCategory.anti_debug for f in findings):
            recommendations.append("Use anti-anti-debug patches or emulation")
        if any(f.category == FindingCategory.anti_frida for f in findings):
            recommendations.append("Use modified Frida build or stalker mode")

        execution_time = int((time.time() - start_time) * 1000)

        # Context data for next stages
        context_data = {
            "is_packed": any(f.category == FindingCategory.packing for f in findings),
            "has_anti_debug": any(f.category == FindingCategory.anti_debug for f in findings),
            "has_anti_vm": any(f.category == FindingCategory.anti_vm for f in findings),
            "has_anti_frida": any(f.category == FindingCategory.anti_frida for f in findings),
            "overall_entropy": overall_entropy,
            "detection_count": len(findings),
            "umbriel_risk_score": risk_score
        }

        return PluginResult(
            findings=findings,
            artifacts=artifacts,
            events=events,
            success=True,
            execution_time_ms=execution_time,
            risk_score=risk_score,
            recommendations=recommendations,
            context_data=context_data
        )

    def _find_pattern(
        self,
        data: bytes,
        pattern: bytes,
        mask: Optional[bytes] = None
    ) -> List[int]:
        """Find all occurrences of a pattern in data."""
        matches = []

        if mask is None:
            # Simple search
            offset = 0
            while True:
                pos = data.find(pattern, offset)
                if pos == -1:
                    break
                matches.append(pos)
                offset = pos + 1
        else:
            # Masked search
            for i in range(len(data) - len(pattern) + 1):
                match = True
                for j, (pat_byte, mask_byte) in enumerate(zip(pattern, mask)):
                    if (data[i + j] & mask_byte) != (pat_byte & mask_byte):
                        match = False
                        break
                if match:
                    matches.append(i)

        return matches

    def _calculate_risk_score(self, findings: List[Finding]) -> float:
        """Calculate overall risk score from findings."""
        if not findings:
            return 0.0

        # Weight by severity
        weights = {
            Severity.info: 0.1,
            Severity.low: 0.2,
            Severity.medium: 0.4,
            Severity.high: 0.7,
            Severity.critical: 1.0
        }

        total_weight = sum(weights.get(f.severity, 0.5) * f.confidence for f in findings)

        # Normalize to 0-1 range (cap at 1.0)
        normalized = min(total_weight / 10.0, 1.0)

        # Boost if multiple categories detected
        categories = set(f.category for f in findings)
        if len(categories) >= 3:
            normalized = min(normalized + 0.2, 1.0)

        return round(normalized, 2)

    def _generate_artifacts(
        self,
        ctx: JobContext,
        findings: List[Finding],
        overall_entropy: float,
        section_entropies: List[Dict]
    ) -> List[Artifact]:
        """Generate output artifacts."""
        import json

        artifacts = []

        # Main JSON report
        report = {
            "plugin": "umbriel",
            "version": self.version,
            "target": ctx.target_path,
            "summary": {
                "total_findings": len(findings),
                "by_severity": {
                    s.value: sum(1 for f in findings if f.severity == s)
                    for s in Severity
                },
                "by_category": {},
                "overall_entropy": overall_entropy
            },
            "findings": [
                {
                    "id": str(f.id),
                    "severity": f.severity.value,
                    "category": f.category.value,
                    "title": f.title,
                    "description": f.description,
                    "confidence": f.confidence,
                    "evidence": [e.model_dump() for e in f.evidence],
                    "tags": f.tags
                }
                for f in findings
            ]
        }

        # Count by category
        for f in findings:
            cat = f.category.value
            report["summary"]["by_category"][cat] = report["summary"]["by_category"].get(cat, 0) + 1

        report_path = ctx.get_artifact_path("anti_analysis_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        report_content = json.dumps(report)
        artifacts.append(Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.json,
            name="anti_analysis_report.json",
            description="Umbriel anti-analysis detection report",
            uri=f"file://{report_path}",
            sha256=hashlib.sha256(report_content.encode()).hexdigest(),
            size_bytes=len(report_content),
            meta={"findings": len(findings)}
        ))

        # Entropy profile artifact (if computed)
        if section_entropies:
            entropy_data = {
                "overall_entropy": overall_entropy,
                "sections": section_entropies
            }
            entropy_path = ctx.get_artifact_path("entropy_profile.json")
            with open(entropy_path, "w") as f:
                json.dump(entropy_data, f, indent=2)

            artifacts.append(Artifact(
                job_id=ctx.job.id,
                artifact_type=ArtifactType.json,
                name="entropy_profile.json",
                description="Binary entropy profile by section",
                uri=f"file://{entropy_path}",
                meta={"overall_entropy": overall_entropy}
            ))

        return artifacts
