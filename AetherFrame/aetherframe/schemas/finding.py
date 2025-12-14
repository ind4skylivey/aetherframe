"""Finding schema — security-relevant observations from analysis.

Findings are the core intelligence output:
- Anti-analysis detections
- Behavioral patterns
- Diff anomalies
- Intent classifications
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class Severity(str, Enum):
    """Finding severity levels (CVSS-aligned)."""
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class FindingCategory(str, Enum):
    """Finding categories aligned with ecosystem modules."""
    # Umbriel
    anti_debug = "anti-debug"
    anti_vm = "anti-vm"
    anti_frida = "anti-frida"
    anti_emulator = "anti-emulator"
    packing = "packing"
    obfuscation = "obfuscation"
    timing_check = "timing-check"
    # Valkyrie
    binary_diff = "binary-diff"
    function_change = "function-change"
    new_code = "new-code"
    removed_code = "removed-code"
    risk_delta = "risk-delta"
    # Mnemosyne
    memory_anomaly = "memory-anomaly"
    state_transition = "state-transition"
    heap_spray = "heap-spray"
    stack_pivot = "stack-pivot"
    # Noema
    intent_malicious = "intent-malicious"
    intent_evasive = "intent-evasive"
    intent_persistence = "intent-persistence"
    intent_exfiltration = "intent-exfiltration"
    intent_exploitation = "intent-exploitation"
    # LainTrace
    runtime_hook = "runtime-hook"
    syscall_anomaly = "syscall-anomaly"
    # Generic
    static = "static"
    dynamic = "dynamic"
    heuristic = "heuristic"


class Evidence(BaseModel):
    """Structured evidence supporting a finding."""
    type: str  # "bytes", "address", "function", "string", "pattern"
    location: Optional[str] = None  # File offset, memory address, function name
    value: Optional[str] = None  # The actual data
    context: Optional[str] = None  # Surrounding context
    reference: Optional[str] = None  # Link to artifact or external ref


class FindingCreate(BaseModel):
    """Schema for creating a finding."""
    job_id: int
    severity: Severity
    category: FindingCategory
    title: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(default=None, max_length=4096)
    evidence: List[Evidence] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    """Complete finding representation."""
    id: Optional[int] = None
    job_id: int
    severity: Severity
    category: FindingCategory
    title: str
    description: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    plugin_id: Optional[str] = None
    stage: Optional[str] = None
    created_at: datetime = Field(default_factory=_utc_now)
    meta: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "job_id": 123,
                "severity": "high",
                "category": "anti-debug",
                "title": "IsDebuggerPresent API detected",
                "description": "Binary calls IsDebuggerPresent at 0x401234",
                "evidence": [
                    {
                        "type": "function",
                        "location": "0x401234",
                        "value": "call kernel32.IsDebuggerPresent",
                        "context": "Anti-debug check in main()"
                    }
                ],
                "confidence": 0.95,
                "tags": ["anti-debug", "kernel32", "windows"],
                "plugin_id": "umbriel",
                "stage": "gate"
            }
        }
    )

    @property
    def risk_score(self) -> float:
        """Calculate risk score from severity and confidence."""
        severity_weights = {
            Severity.info: 0.1,
            Severity.low: 0.3,
            Severity.medium: 0.5,
            Severity.high: 0.8,
            Severity.critical: 1.0
        }
        return severity_weights.get(self.severity, 0.5) * self.confidence
