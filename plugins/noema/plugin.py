"""Noema — Intent Inference Engine.

Noema (from Greek νόημα, "thought" or "meaning") is the final stage
in the analysis pipeline. It synthesizes findings from all previous
stages to infer the INTENT of the analyzed software.

Key principles:
1. NO BLACK BOX: Every classification has an explainable chain of evidence
2. AUDITABLE: All reasoning is logged and can be reviewed
3. TAXONOMY-BASED: Uses established frameworks (MITRE ATT&CK)
4. CONFIDENCE-AWARE: Every inference has a confidence score

Named after Husserl's phenomenological concept of the "object of thought."
"""

from __future__ import annotations
import json
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import UUID

from aetherframe.plugins.base import Plugin, PluginManifest, PluginValidationError
from aetherframe.schemas import (
    JobContext, PluginResult,
    Finding, Severity, FindingCategory, Evidence,
    Artifact, ArtifactType,
    TraceEvent, EventSource, EventType
)


# ============================================================================
# INTENT TAXONOMY (MITRE ATT&CK aligned)
# ============================================================================

class IntentCategory(str, Enum):
    """High-level intent categories."""
    # Execution
    execution = "execution"
    # Persistence
    persistence = "persistence"
    # Privilege Escalation
    privilege_escalation = "privilege_escalation"
    # Defense Evasion
    defense_evasion = "defense_evasion"
    # Credential Access
    credential_access = "credential_access"
    # Discovery
    discovery = "discovery"
    # Lateral Movement
    lateral_movement = "lateral_movement"
    # Collection
    collection = "collection"
    # Command and Control
    command_and_control = "command_and_control"
    # Exfiltration
    exfiltration = "exfiltration"
    # Impact
    impact = "impact"
    # Benign
    benign = "benign"
    # Unknown
    unknown = "unknown"


@dataclass
class IntentIndicator:
    """An indicator that contributes to an intent classification."""
    id: str
    name: str
    category: IntentCategory
    weight: float  # 0.0 to 1.0, contribution to final score
    description: str
    evidence_types: List[str]  # Types of evidence that trigger this
    mitre_id: Optional[str] = None  # MITRE ATT&CK ID if applicable


# MITRE ATT&CK aligned indicators
INTENT_INDICATORS: List[IntentIndicator] = [
    # Defense Evasion (T1027, T1055, T1070)
    IntentIndicator(
        id="IE001",
        name="Anti-Debug Behavior",
        category=IntentCategory.defense_evasion,
        weight=0.8,
        description="Software actively detects and evades debugging",
        evidence_types=["anti-debug", "FindingCategory.anti_debug"],
        mitre_id="T1622"
    ),
    IntentIndicator(
        id="IE002",
        name="Anti-VM Behavior",
        category=IntentCategory.defense_evasion,
        weight=0.9,
        description="Software detects virtualized environments",
        evidence_types=["anti-vm", "FindingCategory.anti_vm"],
        mitre_id="T1497"
    ),
    IntentIndicator(
        id="IE003",
        name="Anti-Analysis Tools",
        category=IntentCategory.defense_evasion,
        weight=0.95,
        description="Software detects analysis tools like Frida",
        evidence_types=["anti-frida", "FindingCategory.anti_frida"],
        mitre_id="T1622"
    ),
    IntentIndicator(
        id="IE004",
        name="Packing/Obfuscation",
        category=IntentCategory.defense_evasion,
        weight=0.7,
        description="Software uses packing or obfuscation",
        evidence_types=["packing", "entropy", "FindingCategory.packing"],
        mitre_id="T1027"
    ),

    # Execution (T1059, T1106)
    IntentIndicator(
        id="IE010",
        name="Process Injection",
        category=IntentCategory.execution,
        weight=0.95,
        description="Software injects code into other processes",
        evidence_types=["CreateRemoteThread", "WriteProcessMemory", "VirtualAllocEx"],
        mitre_id="T1055"
    ),
    IntentIndicator(
        id="IE011",
        name="DLL Injection",
        category=IntentCategory.execution,
        weight=0.85,
        description="Software loads DLLs into other processes",
        evidence_types=["LoadLibrary", "GetProcAddress"],
        mitre_id="T1055.001"
    ),

    # Persistence (T1547, T1053)
    IntentIndicator(
        id="IE020",
        name="Registry Persistence",
        category=IntentCategory.persistence,
        weight=0.8,
        description="Software modifies registry for persistence",
        evidence_types=["RegSetValueEx", "RegCreateKey", "CurrentVersion\\Run"],
        mitre_id="T1547.001"
    ),
    IntentIndicator(
        id="IE021",
        name="Service Creation",
        category=IntentCategory.persistence,
        weight=0.85,
        description="Software creates services for persistence",
        evidence_types=["CreateService", "StartService", "OpenSCManager"],
        mitre_id="T1543.003"
    ),

    # Command and Control (T1071)
    IntentIndicator(
        id="IE030",
        name="Network Communication",
        category=IntentCategory.command_and_control,
        weight=0.6,
        description="Software establishes network connections",
        evidence_types=["WSAStartup", "connect", "socket", "HttpOpenRequest"],
        mitre_id="T1071"
    ),
    IntentIndicator(
        id="IE031",
        name="Encrypted C2",
        category=IntentCategory.command_and_control,
        weight=0.8,
        description="Software uses encryption for C2",
        evidence_types=["CryptEncrypt", "CryptDecrypt", "SSL", "TLS"],
        mitre_id="T1573"
    ),

    # Credential Access (T1003, T1555)
    IntentIndicator(
        id="IE040",
        name="Credential Dumping",
        category=IntentCategory.credential_access,
        weight=0.95,
        description="Software accesses credential stores",
        evidence_types=["lsass", "SAM", "NTDS", "password", "credential"],
        mitre_id="T1003"
    ),
    IntentIndicator(
        id="IE041",
        name="Browser Credential Access",
        category=IntentCategory.credential_access,
        weight=0.85,
        description="Software accesses browser credential stores",
        evidence_types=["Login Data", "cookies.sqlite", "Chrome", "Firefox"],
        mitre_id="T1555.003"
    ),

    # Collection (T1005, T1113)
    IntentIndicator(
        id="IE050",
        name="Screen Capture",
        category=IntentCategory.collection,
        weight=0.75,
        description="Software captures screen contents",
        evidence_types=["GetDC", "BitBlt", "CreateCompatibleBitmap"],
        mitre_id="T1113"
    ),
    IntentIndicator(
        id="IE051",
        name="Keylogging",
        category=IntentCategory.collection,
        weight=0.9,
        description="Software captures keystrokes",
        evidence_types=["SetWindowsHookEx", "GetAsyncKeyState", "GetKeyState"],
        mitre_id="T1056.001"
    ),

    # Exfiltration (T1041)
    IntentIndicator(
        id="IE060",
        name="Data Exfiltration",
        category=IntentCategory.exfiltration,
        weight=0.85,
        description="Software exfiltrates data over network",
        evidence_types=["send", "HttpSendRequest", "POST", "upload"],
        mitre_id="T1041"
    ),

    # Impact (T1486, T1489)
    IntentIndicator(
        id="IE070",
        name="Ransomware Indicators",
        category=IntentCategory.impact,
        weight=0.95,
        description="Software shows ransomware behavior",
        evidence_types=["ransom", "bitcoin", "encrypt", "decrypt", ".locked"],
        mitre_id="T1486"
    ),
    IntentIndicator(
        id="IE071",
        name="Data Destruction",
        category=IntentCategory.impact,
        weight=0.9,
        description="Software destroys data",
        evidence_types=["DeleteFile", "wipe", "shred", "overwrite"],
        mitre_id="T1485"
    ),
]


# ============================================================================
# FEATURE EXTRACTION
# ============================================================================

@dataclass
class FeatureVector:
    """Extracted features for intent classification."""
    # Binary features
    has_anti_debug: bool = False
    has_anti_vm: bool = False
    has_anti_frida: bool = False
    has_packing: bool = False
    high_entropy: bool = False

    # API features
    api_categories: Dict[str, int] = field(default_factory=dict)
    suspicious_apis: List[str] = field(default_factory=list)

    # String features
    suspicious_strings: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)

    # Behavioral features
    creates_files: bool = False
    modifies_registry: bool = False
    network_activity: bool = False
    process_injection: bool = False

    # From other modules
    umbriel_risk: float = 0.0
    valkyrie_risk: float = 0.0
    mnemosyne_anomalies: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "anti_debug": self.has_anti_debug,
            "anti_vm": self.has_anti_vm,
            "anti_frida": self.has_anti_frida,
            "packing": self.has_packing,
            "high_entropy": self.high_entropy,
            "api_categories": self.api_categories,
            "suspicious_apis": self.suspicious_apis,
            "suspicious_strings": self.suspicious_strings,
            "urls": self.urls,
            "creates_files": self.creates_files,
            "modifies_registry": self.modifies_registry,
            "network_activity": self.network_activity,
            "process_injection": self.process_injection
        }


def extract_features(ctx: JobContext) -> FeatureVector:
    """Extract features from previous stage outputs."""
    features = FeatureVector()

    # From pipeline context (Umbriel output)
    pipeline_ctx = ctx.pipeline_context
    features.has_anti_debug = pipeline_ctx.get("has_anti_debug", False)
    features.has_anti_vm = pipeline_ctx.get("has_anti_vm", False)
    features.has_anti_frida = pipeline_ctx.get("has_anti_frida", False)
    features.has_packing = pipeline_ctx.get("is_packed", False)
    features.high_entropy = pipeline_ctx.get("overall_entropy", 0.0) >= 7.0
    features.umbriel_risk = pipeline_ctx.get("umbriel_risk_score", 0.0)
    features.valkyrie_risk = pipeline_ctx.get("overall_risk", 0.0)

    # From previous findings
    for finding in ctx.previous_findings:
        category = finding.get("category", "")

        if "anti-debug" in category:
            features.has_anti_debug = True
        elif "anti-vm" in category:
            features.has_anti_vm = True
        elif "anti-frida" in category:
            features.has_anti_frida = True
        elif "packing" in category:
            features.has_packing = True

        # Extract evidence
        for evidence in finding.get("evidence", []):
            value = evidence.get("value", "")
            if value:
                # Check for suspicious APIs
                for api in ["CreateRemoteThread", "WriteProcessMemory",
                           "VirtualAllocEx", "SetWindowsHookEx"]:
                    if api.lower() in value.lower():
                        features.suspicious_apis.append(api)
                        features.process_injection = True

                # Check for network APIs
                for api in ["WSAStartup", "connect", "socket", "send", "recv"]:
                    if api.lower() in value.lower():
                        features.network_activity = True

                # Check for persistence
                for api in ["RegSetValueEx", "CreateService"]:
                    if api.lower() in value.lower():
                        features.modifies_registry = True

    return features


# ============================================================================
# INTENT CLASSIFICATION
# ============================================================================

@dataclass
class IntentClassification:
    """A classified intent with explanation."""
    category: IntentCategory
    confidence: float
    evidence_chain: List[str]  # Chain of reasoning
    contributing_indicators: List[str]
    mitre_ids: List[str]
    severity: Severity

    def explain(self) -> str:
        """Generate human-readable explanation."""
        lines = [
            f"Intent: {self.category.value.replace('_', ' ').title()}",
            f"Confidence: {self.confidence:.0%}",
            f"Severity: {self.severity.value}",
            "",
            "Evidence Chain:"
        ]
        for i, evidence in enumerate(self.evidence_chain, 1):
            lines.append(f"  {i}. {evidence}")

        if self.mitre_ids:
            lines.append("")
            lines.append(f"MITRE ATT&CK: {', '.join(self.mitre_ids)}")

        return "\n".join(lines)


def classify_intent(features: FeatureVector, depth: str = "deep") -> List[IntentClassification]:
    """Classify intents based on extracted features."""
    classifications = []
    category_scores: Dict[IntentCategory, Tuple[float, List[str], List[str], List[str]]] = \
        defaultdict(lambda: (0.0, [], [], []))

    # Score each indicator
    for indicator in INTENT_INDICATORS:
        triggered = False
        evidence = []

        # Check evidence types
        for evidence_type in indicator.evidence_types:
            # Check boolean features
            if evidence_type == "anti-debug" and features.has_anti_debug:
                triggered = True
                evidence.append("Anti-debug techniques detected")
            elif evidence_type == "anti-vm" and features.has_anti_vm:
                triggered = True
                evidence.append("Anti-VM techniques detected")
            elif evidence_type == "anti-frida" and features.has_anti_frida:
                triggered = True
                evidence.append("Anti-Frida techniques detected")
            elif evidence_type in ("packing", "entropy") and features.has_packing:
                triggered = True
                evidence.append("Packing/obfuscation detected")

            # Check suspicious APIs
            for api in features.suspicious_apis:
                if evidence_type.lower() in api.lower():
                    triggered = True
                    evidence.append(f"Suspicious API: {api}")

            # Check suspicious strings
            for s in features.suspicious_strings:
                if evidence_type.lower() in s.lower():
                    triggered = True
                    evidence.append(f"Suspicious string: {s}")

        if triggered:
            cat = indicator.category
            current_score, current_evidence, current_indicators, current_mitre = \
                category_scores[cat]

            new_score = current_score + indicator.weight
            new_evidence = current_evidence + evidence
            new_indicators = current_indicators + [indicator.name]
            new_mitre = current_mitre
            if indicator.mitre_id:
                new_mitre = current_mitre + [indicator.mitre_id]

            category_scores[cat] = (new_score, new_evidence, new_indicators, new_mitre)

    # Boost defense evasion if multiple types detected
    if features.has_anti_debug and features.has_anti_vm:
        current = category_scores[IntentCategory.defense_evasion]
        category_scores[IntentCategory.defense_evasion] = (
            current[0] + 0.5,
            current[1] + ["Multiple evasion techniques combined"],
            current[2],
            current[3]
        )

    # Normalize scores and create classifications
    max_score = max((s[0] for s in category_scores.values()), default=0.0) or 1.0

    for category, (score, evidence, indicators, mitre) in category_scores.items():
        if score > 0:
            confidence = min(score / max_score, 1.0)

            # Determine severity
            if confidence >= 0.8:
                severity = Severity.critical
            elif confidence >= 0.6:
                severity = Severity.high
            elif confidence >= 0.4:
                severity = Severity.medium
            else:
                severity = Severity.low

            classifications.append(IntentClassification(
                category=category,
                confidence=confidence,
                evidence_chain=evidence,
                contributing_indicators=indicators,
                mitre_ids=list(set(mitre)),
                severity=severity
            ))

    # Sort by confidence
    classifications.sort(key=lambda c: c.confidence, reverse=True)

    return classifications


# ============================================================================
# NOEMA PLUGIN
# ============================================================================

class NoemaPlugin(Plugin):
    """Noema Intent Inference Plugin.

    The final stage in the analysis pipeline that synthesizes
    all findings into actionable intent classifications.
    """

    def validate(self, ctx: JobContext) -> None:
        """Validate we have data to analyze."""
        # Noema can work with:
        # - Previous findings (from Umbriel, Valkyrie, etc.)
        # - Pipeline context
        # - Raw binary (for fallback analysis)
        pass

    def run(self, ctx: JobContext) -> PluginResult:
        """Execute intent inference."""
        import time
        start_time = time.time()

        findings: List[Finding] = []
        artifacts: List[Artifact] = []
        events: List[TraceEvent] = []

        depth = self.config.get("depth", "deep")
        explain = self.config.get("explain", True)
        confidence_threshold = self.config.get("confidence_threshold", 0.5)
        taxonomy = self.config.get("taxonomy", "mitre_attack")

        # Emit start event
        events.append(TraceEvent(
            job_id=ctx.job.id,
            source=EventSource.noema,
            event_type=EventType.info,
            payload={"action": "inference_start", "depth": depth}
        ))

        # Extract features
        features = extract_features(ctx)

        # Classify intents
        classifications = classify_intent(features, depth)

        # Filter by confidence threshold
        significant = [c for c in classifications if c.confidence >= confidence_threshold]

        # Generate findings from classifications
        for classification in significant:
            category_map = {
                IntentCategory.defense_evasion: FindingCategory.intent_evasive,
                IntentCategory.execution: FindingCategory.intent_malicious,
                IntentCategory.persistence: FindingCategory.intent_persistence,
                IntentCategory.credential_access: FindingCategory.intent_malicious,
                IntentCategory.exfiltration: FindingCategory.intent_exfiltration,
                IntentCategory.impact: FindingCategory.intent_malicious,
                IntentCategory.command_and_control: FindingCategory.intent_malicious,
            }

            finding_category = category_map.get(
                classification.category, FindingCategory.heuristic
            )

            findings.append(Finding(
                job_id=ctx.job.id,
                severity=classification.severity,
                category=finding_category,
                title=f"Intent: {classification.category.value.replace('_', ' ').title()}",
                description=classification.explain() if explain else None,
                evidence=[
                    Evidence(
                        type="inference",
                        value="; ".join(classification.evidence_chain[:5]),
                        context=f"MITRE: {', '.join(classification.mitre_ids)}" if classification.mitre_ids else None
                    )
                ],
                confidence=classification.confidence,
                tags=["noema", classification.category.value] + classification.mitre_ids
            ))

        # Calculate overall threat score
        threat_score = 0.0
        if significant:
            # Weighted average with severity boost
            severity_weights = {
                Severity.info: 0.1,
                Severity.low: 0.3,
                Severity.medium: 0.5,
                Severity.high: 0.8,
                Severity.critical: 1.0
            }
            weighted_sum = sum(
                c.confidence * severity_weights.get(c.severity, 0.5)
                for c in significant
            )
            threat_score = min(weighted_sum / len(significant), 1.0)

        # Generate report artifact
        report = self._generate_report(ctx, features, classifications, threat_score)
        artifacts.append(report)

        # Summary finding
        if significant:
            top_intents = [c.category.value for c in significant[:3]]
            findings.append(Finding(
                job_id=ctx.job.id,
                severity=Severity.info,
                category=FindingCategory.heuristic,
                title=f"Noema analysis: {len(significant)} intent(s) identified",
                description=f"Top intents: {', '.join(top_intents)}. Threat score: {threat_score:.0%}",
                evidence=[Evidence(
                    type="pattern",
                    value=json.dumps({
                        "intent_count": len(significant),
                        "threat_score": threat_score,
                        "top_intents": top_intents
                    })
                )],
                confidence=1.0,
                tags=["noema", "summary"]
            ))
        else:
            findings.append(Finding(
                job_id=ctx.job.id,
                severity=Severity.info,
                category=FindingCategory.heuristic,
                title="No significant malicious intent detected",
                description="Analysis did not find strong indicators of malicious intent",
                confidence=1.0 - max((c.confidence for c in classifications), default=0),
                tags=["noema", "benign"]
            ))

        execution_time = int((time.time() - start_time) * 1000)

        return PluginResult(
            findings=findings,
            artifacts=artifacts,
            events=events,
            success=True,
            execution_time_ms=execution_time,
            risk_score=threat_score,
            context_data={
                "threat_score": threat_score,
                "intents_detected": [c.category.value for c in significant],
                "mitre_techniques": list(set(
                    m for c in significant for m in c.mitre_ids
                ))
            }
        )

    def _generate_report(
        self,
        ctx: JobContext,
        features: FeatureVector,
        classifications: List[IntentClassification],
        threat_score: float
    ) -> Artifact:
        """Generate intent inference report."""
        report = {
            "plugin": "noema",
            "version": self.version,
            "target": ctx.target_path,
            "analysis_time": datetime.utcnow().isoformat(),

            "threat_score": threat_score,
            "threat_level": (
                "critical" if threat_score >= 0.8 else
                "high" if threat_score >= 0.6 else
                "medium" if threat_score >= 0.4 else
                "low" if threat_score >= 0.2 else
                "minimal"
            ),

            "features": features.to_dict(),

            "classifications": [
                {
                    "category": c.category.value,
                    "confidence": c.confidence,
                    "severity": c.severity.value,
                    "evidence_chain": c.evidence_chain,
                    "indicators": c.contributing_indicators,
                    "mitre_ids": c.mitre_ids
                }
                for c in classifications
            ],

            "mitre_coverage": list(set(
                m for c in classifications for m in c.mitre_ids
            )),

            "recommendations": self._generate_recommendations(classifications, threat_score)
        }

        path = ctx.get_artifact_path("intent_report.json")
        with open(path, "w") as f:
            json.dump(report, f, indent=2)

        return Artifact(
            job_id=ctx.job.id,
            artifact_type=ArtifactType.report,
            name="intent_report.json",
            description="Noema intent inference report",
            uri=f"file://{path}",
            meta={
                "threat_score": threat_score,
                "classifications": len(classifications)
            }
        )

    def _generate_recommendations(
        self,
        classifications: List[IntentClassification],
        threat_score: float
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if threat_score >= 0.8:
            recommendations.append("CRITICAL: Immediate isolation and forensic analysis recommended")

        categories = set(c.category for c in classifications)

        if IntentCategory.defense_evasion in categories:
            recommendations.append("Use specialized anti-evasion tools for deeper analysis")

        if IntentCategory.persistence in categories:
            recommendations.append("Check system for persistence mechanisms (registry, services)")

        if IntentCategory.credential_access in categories:
            recommendations.append("Rotate credentials on potentially compromised systems")

        if IntentCategory.exfiltration in categories:
            recommendations.append("Review network logs for data exfiltration attempts")

        if IntentCategory.command_and_control in categories:
            recommendations.append("Block identified C2 indicators at network perimeter")

        if IntentCategory.impact in categories:
            recommendations.append("Ensure backups are available and isolated")

        if not recommendations:
            recommendations.append("Continue standard security monitoring")

        return recommendations
