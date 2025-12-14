# AetherFrame Ecosystem Architecture

## Overview

AetherFrame is a **complete reverse engineering laboratory** — not a single tool.
It functions as a **BUS** (data + events), **ORCHESTRATOR** (pipelines), and **CONTRACT ENFORCER** (plugins).

```
AetherFrame (framework / orchestrator)
 ├── Reveris Noctis (UI + CLI + report engine)
 ├── LainTrace (dynamic tracing / Frida hooks)
 ├── Umbriel (anti-analysis detector)
 ├── Valkyrie (binary diff / evolution tracker)
 ├── Mnemosyne (memory + state reconstruction)
 └── Noema (intent inference engine)
```

---

## Core Philosophy

### AetherFrame exposes:

- **Jobs** — Units of analysis work
- **Artifacts** — Output files (reports, graphs, dumps)
- **Findings** — Security-relevant observations
- **TraceEvents** — Runtime events from dynamic analysis

### AetherFrame NEVER relies on:

- Ad-hoc prints
- Tool-specific outputs
- UI knowledge of internals

### Reveris Noctis:

- Only consumes the API
- Optionally subscribes to live events
- Renders findings, timelines, diffs, and reports

---

## Data Model

### Job

```json
{
  "id": "uuid",
  "target": "path|pid",
  "target_type": "binary|apk|pid|memory_dump",
  "status": "pending|running|done|failed",
  "pipeline_id": "quicklook|deep-static|...",
  "created_by": "user",
  "created_at": "timestamp"
}
```

### Artifact

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "artifact_type": "json|html|dump|graph|timeline",
  "name": "report.json",
  "uri": "s3://bucket/path",
  "sha256": "hex",
  "plugin_id": "umbriel",
  "stage": "gate"
}
```

### Finding

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "severity": "info|low|medium|high|critical",
  "category": "anti-debug|binary-diff|intent-malicious|...",
  "title": "string",
  "description": "string",
  "evidence": [{"type": "...", "location": "...", "value": "..."}],
  "confidence": 0.0-1.0,
  "tags": ["tag1", "tag2"]
}
```

### TraceEvent

```json
{
  "id": "uuid",
  "job_id": "uuid",
  "ts": "timestamp",
  "source": "laintrace|mnemosyne|...",
  "event_type": "hook_enter|state_change|memory_write|...",
  "symbol": "function_name",
  "address": "0x...",
  "payload": {}
}
```

---

## Plugin Contract

### Manifest (plugin.yaml)

```yaml
id: plugin_id
name: Plugin Name
version: 0.1.0
kind: detector|differ|tracer|reconstructor|inferencer|analyzer
capabilities:
  - capability.name
inputs:
  - type: binary
outputs:
  - type: findings
  - type: artifacts
```

### Runtime Interface

```python
class Plugin(ABC):
    def validate(self, ctx: JobContext) -> None: ...
    def run(self, ctx: JobContext) -> PluginResult: ...
```

### PluginResult

```python
class PluginResult:
    findings: List[Finding]
    artifacts: List[Artifact]
    events: List[TraceEvent]
    success: bool
    risk_score: Optional[float]
    context_data: Dict[str, Any]  # Passed to next stage
```

---

## Module Responsibilities

### Umbriel (Anti-Analysis Detector)

- Runs FIRST as a gate
- Detects: anti-debug, anti-VM, anti-Frida, packing, timing checks
- Outputs: risk score, recommendations for pipeline selection
- Artifacts: `anti_analysis_report.json`, `entropy_profile.json`

### Valkyrie (Binary Diff Engine)

- Semantic function-level diffing
- Risk scoring for code changes
- Artifacts: `diff_report.json`, `diff_heatmap.json`
- Triggers LainTrace on high-risk deltas

### Mnemosyne (Memory & State Reconstruction)

- Consumes TraceEvents from LainTrace
- Builds execution timelines
- Constructs state transition graphs
- Detects memory anomalies (heap spray, RWX)
- Artifacts: `state_timeline.json`, `state_graph.json`, `state_graph.dot`

### Noema (Intent Inference Engine)

- Final stage in all pipelines
- Synthesizes findings into intent classifications
- Maps to MITRE ATT&CK taxonomy
- Explainable evidence chains
- Artifacts: `intent_report.json`

### LainTrace (Dynamic Tracing)

- Frida-based hooking
- Function, syscall, and memory tracing
- Outputs TraceEvents to Mnemosyne
- Artifacts: `trace_log.json`

---

## Pipelines

### quicklook (Fast Triage)

```
Umbriel(gate) → StaticAnalyzer → Noema(shallow)
```

### deep-static (Comprehensive Static)

```
StaticAnalyzer → Umbriel(thorough) → Noema(deep)
```

### dynamic-first (Dynamic Analysis)

```
Umbriel(gate) → LainTrace → Mnemosyne → Noema(deep+traces)
```

### release-watch (Evolution Tracking)

```
Valkyrie(diff) → RiskScore → [LainTrace if high-risk] → Noema
```

### full-audit (Everything)

```
Umbriel → StaticAnalyzer → LainTrace → Mnemosyne → Noema
```

---

## Reveris Noctis Integration

### CLI Commands

```bash
reveris run --pipeline quicklook --file sample.exe
reveris diff --a v1.exe --b v2.exe
reveris trace sample.exe --profile strict
reveris report job-id --format pdf
reveris jobs list
reveris plugins list
```

### UI Views

- **Dashboard** — Job overview, pipeline status
- **Findings** — By category, severity, MITRE technique
- **Timeline** — Mnemosyne execution timeline
- **Diff** — Valkyrie binary comparison heatmap
- **Intent** — Noema threat gauge and classifications

---

## Repository Structure

```
AetherFrame/
  aetherframe/
    plugins/
      umbriel/
        __init__.py
        plugin.yaml
        plugin.py
      valkyrie/
      mnemosyne/
      noema/
      laintrace/
      static_analyzer/
    core/
      pipeline.py
      orchestrator.py
      repository.py
    schemas/
      job.py
      artifact.py
      finding.py
      trace_event.py
      plugin_result.py
    api/
      main.py
    tests/
      test_umbriel.py
      test_integration.py

ReverisNoctis/
  cli/
    main.py
  renderer/
    templates/
      anti_analysis.html
      diff.html
      memory.html
      intent.html
  src/
    ...

LainTrace/
  engine/
    main.py
```

---

## Services (Development)

| Service  | Port      | Description          |
| -------- | --------- | -------------------- |
| API      | 8000      | FastAPI core         |
| Redis    | 6379      | Celery broker        |
| Postgres | 5432      | Persistence          |
| MinIO    | 9000/9001 | Artifact storage     |
| UI       | 3000      | Vite/React dashboard |

---

## Security Considerations

- Plugins run in isolated contexts
- Findings have confidence scores
- Evidence chains are auditable
- No black-box ML claims
- All analysis is explainable
