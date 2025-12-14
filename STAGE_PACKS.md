# AetherFrame Ecosystem — Stage Pack Definitions

## Overview

This document defines the staged implementation of the complete AetherFrame reverse engineering laboratory.
Each stage builds upon previous stages and includes specific acceptance criteria.

---

## STAGE_8: Umbriel (Anti-Analysis Detector)

### Files Created

```
AetherFrame/aetherframe/plugins/umbriel/
├── __init__.py
├── plugin.yaml
└── plugin.py

AetherFrame/aetherframe/schemas/
├── __init__.py
├── job.py
├── artifact.py
├── finding.py
├── trace_event.py
└── plugin_result.py

AetherFrame/aetherframe/plugins/
├── __init__.py
├── base.py
└── registry.py

ReverisNoctis/renderer/templates/
└── anti_analysis.html
```

### Tests Added

```python
# tests/test_umbriel.py
def test_umbriel_manifest_valid()
def test_umbriel_detects_anti_debug()
def test_umbriel_detects_packing()
def test_umbriel_entropy_calculation()
def test_umbriel_generates_artifacts()
```

### Acceptance Criteria

- [ ] Umbriel plugin loads via registry
- [ ] Manifest validation passes
- [ ] Detects IsDebuggerPresent pattern in test binary
- [ ] Detects VMware/VirtualBox strings
- [ ] Computes entropy >= 7.0 for packed samples
- [ ] Generates anti_analysis_report.json artifact
- [ ] Risk score calculation correct
- [ ] HTML template renders findings correctly

---

## STAGE_9: Valkyrie (Binary Diff Engine)

### Files Created

```
AetherFrame/aetherframe/plugins/valkyrie/
├── __init__.py
├── plugin.yaml
└── plugin.py

ReverisNoctis/renderer/templates/
└── diff.html
```

### Tests Added

```python
# tests/test_valkyrie.py
def test_valkyrie_manifest_valid()
def test_valkyrie_binary_metadata_extraction()
def test_valkyrie_function_matching()
def test_valkyrie_diff_detection()
def test_valkyrie_risk_scoring()
def test_valkyrie_heatmap_generation()
```

### Acceptance Criteria

- [ ] Extracts functions from PE/ELF binaries
- [ ] Matches functions by signature hash
- [ ] Detects added/removed/modified functions
- [ ] Generates diff_report.json artifact
- [ ] Generates diff_heatmap.json artifact
- [ ] Risk score increases for suspicious API additions
- [ ] HTML template renders heatmap correctly

---

## STAGE_10: Mnemosyne (Memory & State Reconstruction)

### Files Created

```
AetherFrame/aetherframe/plugins/mnemosyne/
├── __init__.py
├── plugin.yaml
└── plugin.py

ReverisNoctis/renderer/templates/
└── memory.html
```

### Tests Added

```python
# tests/test_mnemosyne.py
def test_mnemosyne_manifest_valid()
def test_mnemosyne_timeline_building()
def test_mnemosyne_state_graph_construction()
def test_mnemosyne_anomaly_detection()
def test_mnemosyne_graphviz_export()
```

### Acceptance Criteria

- [ ] Consumes TraceEvents from LainTrace
- [ ] Builds chronological timeline
- [ ] Constructs state transition graph
- [ ] Detects heap spray patterns
- [ ] Detects RWX memory regions
- [ ] Generates state_timeline.json artifact
- [ ] Generates state_graph.json artifact
- [ ] Generates state_graph.dot artifact
- [ ] HTML template renders timeline correctly

---

## STAGE_11: Noema (Intent Inference Engine)

### Files Created

```
AetherFrame/aetherframe/plugins/noema/
├── __init__.py
├── plugin.yaml
└── plugin.py

ReverisNoctis/renderer/templates/
└── intent.html
```

### Tests Added

```python
# tests/test_noema.py
def test_noema_manifest_valid()
def test_noema_feature_extraction()
def test_noema_intent_classification()
def test_noema_confidence_scoring()
def test_noema_explanation_generation()
def test_noema_mitre_mapping()
```

### Acceptance Criteria

- [ ] Extracts features from Umbriel/Valkyrie output
- [ ] Classifies defense_evasion intent correctly
- [ ] Maps to MITRE ATT&CK technique IDs
- [ ] Generates explainable evidence chains
- [ ] Confidence scores are normalized 0-1
- [ ] Generates intent_report.json artifact
- [ ] HTML template renders threat gauge correctly

---

## STAGE_12: Full Ecosystem Integration

### Files Created

```
AetherFrame/aetherframe/core/
├── pipeline.py
└── orchestrator.py

ReverisNoctis/cli/
└── main.py (updated)
```

### Tests Added

```python
# tests/test_integration.py
def test_pipeline_quicklook()
def test_pipeline_deep_static()
def test_pipeline_dynamic_first()
def test_pipeline_release_watch()
def test_full_audit_pipeline()
def test_cli_run_command()
def test_cli_diff_command()
def test_cli_report_command()
```

### Acceptance Criteria

- [ ] All pipelines execute without error
- [ ] Data flows correctly between stages
- [ ] Findings accumulate across stages
- [ ] Artifacts are persisted to MinIO
- [ ] Events are stored in database
- [ ] CLI commands work end-to-end
- [ ] UI views render correctly
- [ ] Risk scores propagate through pipeline

---

## Verification Commands

```bash
# Run all plugin tests
cd AetherFrame
PYTHONPATH=. pytest tests/test_umbriel.py tests/test_valkyrie.py tests/test_mnemosyne.py tests/test_noema.py -v

# Run integration tests
PYTHONPATH=. pytest tests/test_integration.py -v

# Verify plugin discovery
python -c "from aetherframe.plugins import get_registry; r = get_registry(); print(r.list_plugins())"

# Run quicklook pipeline on test sample
python -m aetherframe.cli run --pipeline quicklook --file tests/samples/test.exe

# CLI smoke test
python ReverisNoctis/cli/main.py status
python ReverisNoctis/cli/main.py plugins list
```

---

## Dependencies

### Python packages (AetherFrame)

```
pyyaml>=6.0
pydantic>=2.0
```

### Python packages (Reveris CLI)

```
typer>=0.9.0
requests>=2.31.0
rich>=13.0  # optional for better output
```

---

## Migration Notes

### Database Migrations

New tables required for full ecosystem:

- `findings` (id, job_id, severity, category, title, evidence, confidence, tags, created_at)
- `artifacts` (id, job_id, type, name, uri, sha256, size_bytes, created_at)
- `trace_events` (id, job_id, ts, source, event_type, payload, thread_id, sequence)

### API Endpoints

New endpoints for findings/artifacts:

- `GET /jobs/{id}/findings`
- `GET /jobs/{id}/artifacts`
- `GET /jobs/{id}/events`
- `GET /jobs/{id}/report`
- `GET /pipelines`
- `GET /pipelines/{id}`

---

## Rollback Plan

Each stage can be rolled back independently by:

1. Removing the plugin directory
2. Removing corresponding test files
3. Reverting CLI/UI additions

The core schemas and infrastructure (Stage 8 base) should remain stable.
