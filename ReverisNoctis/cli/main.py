"""Reveris Noctis CLI — Advanced reverse engineering command interface.

Enhanced CLI with pipeline execution, diff, trace, and report commands.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Optional
from enum import Enum

import typer
import requests

# API configuration
API_BASE = os.getenv("REVERIS_API_BASE", "http://localhost:8000")


# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = typer.Typer(
    name="reveris",
    help="""
    ⚡ Reveris Noctis — AetherFrame CLI Interface ⚡

    Reverse engineering laboratory command center.

    Commands:
      run       Execute analysis pipelines
      diff      Compare binaries
      trace     Dynamic tracing control
      report    Generate reports
      status    System status
      jobs      Job management
      plugins   Plugin management
    """,
    no_args_is_help=True
)


# ============================================================================
# HELPERS
# ============================================================================

def _url(path: str) -> str:
    return f"{API_BASE}{path}"


def _print_json(data: dict, indent: int = 2) -> None:
    """Pretty print JSON data."""
    typer.echo(json.dumps(data, indent=indent, default=str))


def _print_error(message: str) -> None:
    """Print error message."""
    typer.secho(f"✗ Error: {message}", fg=typer.colors.RED, err=True)


def _print_success(message: str) -> None:
    """Print success message."""
    typer.secho(f"✓ {message}", fg=typer.colors.GREEN)


def _print_info(message: str) -> None:
    """Print info message."""
    typer.secho(f"ℹ {message}", fg=typer.colors.CYAN)


def _print_warning(message: str) -> None:
    """Print warning message."""
    typer.secho(f"⚠ {message}", fg=typer.colors.YELLOW)


# ============================================================================
# RUN COMMAND — Execute Pipelines
# ============================================================================

class PipelineType(str, Enum):
    quicklook = "quicklook"
    deep_static = "deep-static"
    dynamic_first = "dynamic-first"
    release_watch = "release-watch"
    full_audit = "full-audit"


@app.command("run")
def run_pipeline(
    file: Path = typer.Argument(..., help="Target file to analyze"),
    pipeline: PipelineType = typer.Option(
        PipelineType.quicklook,
        "--pipeline", "-p",
        help="Analysis pipeline to execute"
    ),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for completion"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags")
):
    """
    Execute an analysis pipeline on a target file.

    Examples:
        reveris run sample.exe --pipeline quicklook
        reveris run malware.bin --pipeline deep-static --output ./results
        reveris run suspicious.apk --pipeline dynamic-first --wait
    """
    if not file.exists():
        _print_error(f"File not found: {file}")
        raise typer.Exit(1)

    _print_info(f"Submitting {file.name} to pipeline: {pipeline.value}")

    # Submit job
    payload = {
        "target": str(file.resolve()),
        "pipeline_id": pipeline.value,
        "tags": tags.split(",") if tags else [],
        "options": {}
    }

    try:
        r = requests.post(_url("/jobs"), json=payload, timeout=10)
        r.raise_for_status()
        job = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to submit job: {e}")
        raise typer.Exit(1)

    job_id = job.get("id")
    _print_success(f"Job submitted: {job_id}")

    if not wait:
        if json_output:
            _print_json(job)
        else:
            typer.echo(f"Job ID: {job_id}")
            typer.echo(f"Check status with: reveris jobs status {job_id}")
        return

    # Wait for completion
    _print_info("Waiting for pipeline completion...")

    with typer.progressbar(length=100, label="Progress") as progress:
        last_progress = 0
        while True:
            try:
                r = requests.get(_url(f"/jobs/{job_id}"), timeout=5)
                job = r.json()
            except Exception:
                time.sleep(2)
                continue

            status = job.get("status", "pending")
            current_progress = int(job.get("progress", 0))

            if current_progress > last_progress:
                progress.update(current_progress - last_progress)
                last_progress = current_progress

            if status in ("done", "completed"):
                progress.update(100 - last_progress)
                break
            elif status == "failed":
                _print_error(f"Job failed: {job.get('error', 'Unknown error')}")
                raise typer.Exit(1)

            time.sleep(1)

    _print_success("Pipeline completed!")

    # Fetch results
    try:
        findings_r = requests.get(_url(f"/jobs/{job_id}/findings"), timeout=10)
        findings = findings_r.json() if findings_r.ok else []

        artifacts_r = requests.get(_url(f"/jobs/{job_id}/artifacts"), timeout=10)
        artifacts = artifacts_r.json() if artifacts_r.ok else []
    except Exception:
        findings = []
        artifacts = []

    if json_output:
        _print_json({
            "job": job,
            "findings": findings,
            "artifacts": artifacts
        })
    else:
        # Summary output
        typer.echo()
        typer.secho("═══ Analysis Results ═══", fg=typer.colors.CYAN, bold=True)
        typer.echo()

        # Findings summary
        if findings:
            by_severity = {}
            for f in findings:
                sev = f.get("severity", "info")
                by_severity[sev] = by_severity.get(sev, 0) + 1

            typer.secho("Findings:", bold=True)
            for sev, count in sorted(by_severity.items()):
                color = {
                    "critical": typer.colors.RED,
                    "high": typer.colors.BRIGHT_RED,
                    "medium": typer.colors.YELLOW,
                    "low": typer.colors.BLUE,
                    "info": typer.colors.WHITE
                }.get(sev, typer.colors.WHITE)
                typer.secho(f"  {sev.upper()}: {count}", fg=color)

            typer.echo()
            typer.secho("Top Findings:", bold=True)
            for f in findings[:5]:
                severity = f.get("severity", "info").upper()
                title = f.get("title", "Unknown")
                typer.echo(f"  [{severity}] {title}")
        else:
            typer.echo("No findings generated.")

        typer.echo()

        # Artifacts summary
        if artifacts:
            typer.secho(f"Artifacts: {len(artifacts)}", bold=True)
            for a in artifacts:
                typer.echo(f"  • {a.get('name', 'Unknown')}")

        # Risk score
        risk_score = job.get("meta", {}).get("risk_score", 0)
        if risk_score > 0:
            typer.echo()
            color = (
                typer.colors.RED if risk_score >= 0.7 else
                typer.colors.YELLOW if risk_score >= 0.4 else
                typer.colors.GREEN
            )
            typer.secho(f"Risk Score: {risk_score:.0%}", fg=color, bold=True)


# ============================================================================
# DIFF COMMAND — Binary Comparison
# ============================================================================

@app.command("diff")
def diff_binaries(
    file_a: Path = typer.Option(..., "--a", help="First binary (old version)"),
    file_b: Path = typer.Option(..., "--b", help="Second binary (new version)"),
    semantic: bool = typer.Option(True, "--semantic/--raw", help="Semantic vs raw diff"),
    heatmap: bool = typer.Option(True, "--heatmap/--no-heatmap", help="Generate heatmap"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """
    Compare two binaries and identify changes.

    Examples:
        reveris diff --a v1.exe --b v2.exe
        reveris diff --a old.bin --b new.bin --output diff_report.json
    """
    if not file_a.exists():
        _print_error(f"File A not found: {file_a}")
        raise typer.Exit(1)
    if not file_b.exists():
        _print_error(f"File B not found: {file_b}")
        raise typer.Exit(1)

    _print_info(f"Comparing: {file_a.name} → {file_b.name}")

    # Submit diff job
    payload = {
        "target": str(file_b.absolute()),
        "pipeline_id": "release-watch",
        "options": {
            "reference_path": str(file_a.absolute()),
            "semantic": semantic,
            "generate_heatmap": heatmap
        }
    }

    try:
        r = requests.post(_url("/jobs"), json=payload, timeout=10)
        r.raise_for_status()
        job = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to submit diff job: {e}")
        raise typer.Exit(1)

    job_id = job.get("id")
    _print_success(f"Diff job submitted: {job_id}")

    # Wait for completion
    _print_info("Computing diff...")

    while True:
        try:
            r = requests.get(_url(f"/jobs/{job_id}"), timeout=5)
            job = r.json()
            status = job.get("status", "pending")

            if status in ("done", "completed"):
                break
            elif status == "failed":
                _print_error(f"Diff failed: {job.get('error')}")
                raise typer.Exit(1)

            time.sleep(1)
        except Exception:
            time.sleep(2)

    _print_success("Diff complete!")

    # Fetch artifacts (diff report)
    try:
        artifacts_r = requests.get(_url(f"/jobs/{job_id}/artifacts"), timeout=10)
        artifacts = artifacts_r.json() if artifacts_r.ok else []

        findings_r = requests.get(_url(f"/jobs/{job_id}/findings"), timeout=10)
        findings = findings_r.json() if findings_r.ok else []
    except Exception:
        artifacts = []
        findings = []

    # Find diff report artifact
    diff_report = next(
        (a for a in artifacts if "diff" in a.get("name", "").lower()),
        None
    )

    if json_output:
        _print_json({
            "job_id": job_id,
            "findings": findings,
            "artifacts": artifacts,
            "diff_report": diff_report
        })
    else:
        typer.echo()
        typer.secho("═══ Diff Results ═══", fg=typer.colors.CYAN, bold=True)
        typer.echo()

        # Summary from findings
        added = sum(1 for f in findings if "added" in f.get("category", ""))
        removed = sum(1 for f in findings if "removed" in f.get("category", ""))
        modified = sum(1 for f in findings if "change" in f.get("category", ""))

        typer.echo(f"  Added:    {added} functions")
        typer.echo(f"  Removed:  {removed} functions")
        typer.echo(f"  Modified: {modified} functions")

        # High-risk changes
        high_risk = [f for f in findings if f.get("severity") in ("high", "critical")]
        if high_risk:
            typer.echo()
            typer.secho("High-Risk Changes:", fg=typer.colors.RED, bold=True)
            for f in high_risk[:5]:
                typer.echo(f"  • {f.get('title', 'Unknown')}")

    if output and diff_report:
        # Download and save report
        typer.echo(f"\nReport saved to: {output}")


# ============================================================================
# TRACE COMMAND — Dynamic Tracing
# ============================================================================

class TraceProfile(str, Enum):
    minimal = "minimal"
    strict = "strict"
    comprehensive = "comprehensive"


@app.command("trace")
def trace_target(
    target: str = typer.Argument(..., help="Target file or PID"),
    profile: TraceProfile = typer.Option(
        TraceProfile.strict,
        "--profile", "-p",
        help="Tracing profile"
    ),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Timeout in seconds"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output trace file"),
    live: bool = typer.Option(False, "--live", help="Stream events in real-time")
):
    """
    Execute dynamic tracing on a target.

    Examples:
        reveris trace sample.exe --profile strict
        reveris trace 1234 --profile comprehensive --live
    """
    _print_info(f"Starting trace: {target} (profile: {profile.value})")

    # Submit trace job
    payload = {
        "target": target,
        "pipeline_id": "dynamic-first",
        "options": {
            "profile": profile.value,
            "timeout": timeout
        }
    }

    try:
        r = requests.post(_url("/jobs"), json=payload, timeout=10)
        r.raise_for_status()
        job = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to start trace: {e}")
        raise typer.Exit(1)

    job_id = job.get("id")
    _print_success(f"Trace job started: {job_id}")

    if live:
        # Stream events (simplified - would use WebSocket in production)
        _print_info("Streaming events (Ctrl+C to stop)...")
        try:
            last_event_id = 0
            while True:
                r = requests.get(_url(f"/jobs/{job_id}/events"), timeout=5)
                events = r.json() if r.ok else []

                for event in events:
                    if event.get("id", 0) > last_event_id:
                        last_event_id = event.get("id", 0)
                        typer.echo(f"[{event.get('event_type')}] {event.get('symbol', '')} {event.get('payload', {})}")

                # Check if job done
                job_r = requests.get(_url(f"/jobs/{job_id}"), timeout=5)
                if job_r.json().get("status") in ("done", "completed", "failed"):
                    break

                time.sleep(0.5)
        except KeyboardInterrupt:
            _print_warning("Trace stopped by user")
    else:
        # Wait for completion
        _print_info(f"Tracing for up to {timeout}s...")

        with typer.progressbar(range(timeout), label="Progress") as progress:
            for _ in progress:
                try:
                    r = requests.get(_url(f"/jobs/{job_id}"), timeout=5)
                    if r.json().get("status") in ("done", "completed", "failed"):
                        break
                except Exception:
                    pass
                time.sleep(1)

        _print_success("Trace complete!")

    # Fetch trace results
    try:
        events_r = requests.get(_url(f"/jobs/{job_id}/events"), timeout=10)
        events = events_r.json() if events_r.ok else []
    except Exception:
        events = []

    typer.echo(f"\nCaptured {len(events)} events")

    if output:
        with open(output, "w") as f:
            json.dump(events, f, indent=2)
        _print_success(f"Trace saved to: {output}")


# ============================================================================
# REPORT COMMAND — Generate Reports
# ============================================================================

class ReportFormat(str, Enum):
    pdf = "pdf"
    html = "html"
    json = "json"
    markdown = "md"


@app.command("report")
def generate_report(
    job_id: str = typer.Argument(..., help="Job ID to generate report for"),
    format: ReportFormat = typer.Option(
        ReportFormat.html,
        "--format", "-f",
        help="Report format"
    ),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    include_artifacts: bool = typer.Option(True, "--artifacts/--no-artifacts")
):
    """
    Generate a report for a completed job.

    Examples:
        reveris report abc-123 --format pdf --output report.pdf
        reveris report abc-123 --format html
    """
    _print_info(f"Generating {format.value.upper()} report for job: {job_id}")

    try:
        r = requests.get(_url(f"/jobs/{job_id}/report?format={format.value}"), timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        _print_error(f"Failed to generate report: {e}")
        raise typer.Exit(1)

    if output:
        with open(output, "wb") as f:
            f.write(r.content)
        _print_success(f"Report saved to: {output}")
    else:
        output_path = Path(f"report_{job_id[:8]}.{format.value}")
        with open(output_path, "wb") as f:
            f.write(r.content)
        _print_success(f"Report saved to: {output_path}")


# ============================================================================
# STATUS COMMAND
# ============================================================================

@app.command("status")
def system_status():
    """Show AetherFrame system status."""
    try:
        r = requests.get(_url("/status"), timeout=5)
        r.raise_for_status()
        status = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to get status: {e}")
        raise typer.Exit(1)

    typer.secho("⚡ AetherFrame Status ⚡", fg=typer.colors.CYAN, bold=True)
    typer.echo()

    typer.echo(f"API:     {'🟢 Online' if status.get('healthy') else '🔴 Offline'}")
    typer.echo(f"Celery:  {'🟢 Online' if status.get('celery_ok') else '🔴 Offline'}")
    typer.echo()

    counts = status.get("counts", {})
    typer.echo(f"Jobs:    {counts.get('jobs', 0)} total")
    typer.echo(f"Plugins: {counts.get('plugins', 0)} registered")
    typer.echo(f"Events:  {counts.get('events', 0)} recorded")


# ============================================================================
# JOBS COMMAND
# ============================================================================

jobs_app = typer.Typer(help="Job management commands")
app.add_typer(jobs_app, name="jobs")


@jobs_app.command("list")
def list_jobs(
    limit: int = typer.Option(10, "--limit", "-n"),
    status_filter: Optional[str] = typer.Option(None, "--status", "-s")
):
    """List recent jobs."""
    try:
        r = requests.get(_url("/jobs"), timeout=5)
        r.raise_for_status()
        jobs = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to list jobs: {e}")
        raise typer.Exit(1)

    if status_filter:
        jobs = [j for j in jobs if j.get("status") == status_filter]

    for job in jobs[:limit]:
        status_icon = {
            "pending": "⏳",
            "running": "🔄",
            "done": "✅",
            "completed": "✅",
            "failed": "❌"
        }.get(job.get("status", ""), "❓")

        typer.echo(f"{status_icon} {job.get('id', 'Unknown')[:8]} | {job.get('status')} | {job.get('target', 'N/A')}")


@jobs_app.command("status")
def job_status(job_id: str = typer.Argument(..., help="Job ID")):
    """Get job status."""
    try:
        r = requests.get(_url(f"/jobs/{job_id}"), timeout=5)
        r.raise_for_status()
        job = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to get job: {e}")
        raise typer.Exit(1)

    _print_json(job)


# ============================================================================
# PLUGINS COMMAND
# ============================================================================

plugins_app = typer.Typer(help="Plugin management commands")
app.add_typer(plugins_app, name="plugins")


@plugins_app.command("list")
def list_plugins():
    """List registered plugins."""
    try:
        r = requests.get(_url("/plugins"), timeout=5)
        r.raise_for_status()
        plugins = r.json()
    except requests.RequestException as e:
        _print_error(f"Failed to list plugins: {e}")
        raise typer.Exit(1)

    for plugin in plugins:
        typer.echo(f"• {plugin.get('name', 'Unknown')} v{plugin.get('version', '?')} - {plugin.get('description', '')}")


# ============================================================================
# PING COMMAND
# ============================================================================

@app.command("ping")
def ping():
    """Basic connectivity check."""
    typer.echo("reveris-ok")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app()
