"""Data access layer."""

from sqlalchemy.orm import Session
from typing import List, Optional, Any

from .models import Job, JobStatus, Plugin, Event, Finding, Artifact, TraceEvent


def create_plugin(db: Session, name: str, version: str, description: str | None) -> Plugin:
    plugin = Plugin(name=name, version=version, description=description)
    db.add(plugin)
    db.commit()
    db.refresh(plugin)
    return plugin


def list_plugins(db: Session) -> List[Plugin]:
    return db.query(Plugin).order_by(Plugin.created_at.desc()).all()


def get_plugin(db: Session, plugin_id: int) -> Optional[Plugin]:
    return db.query(Plugin).filter(Plugin.id == plugin_id).first()


def create_job(db: Session, target: str, plugin_id: Optional[int], pipeline_id: Optional[str] = "quicklook") -> Job:
    job = Job(target=target.strip(), plugin_id=plugin_id, pipeline_id=pipeline_id)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session) -> List[Job]:
    return db.query(Job).order_by(Job.created_at.desc()).all()


def update_job_status(db: Session, job_id: int, status: JobStatus, result=None) -> Optional[Job]:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    job.status = status
    if result is not None:
        job.result = result
    db.commit()
    db.refresh(job)
    return job


def create_event(db: Session, event_type: str, payload, job_id: Optional[int]) -> Event:
    ev = Event(event_type=event_type, payload=payload, job_id=job_id)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


def list_events(db: Session) -> List[Event]:
    return db.query(Event).order_by(Event.created_at.desc()).all()


def create_finding(db: Session, finding_data: Any) -> Finding:
    # finding_data is a Pydantic model (Finding schema)
    # We need to convert it to SQLAlchemy model
    # Note: finding_data.evidence is list of Evidence objects, need to dump

    evidence_dicts = [e.model_dump() for e in finding_data.evidence] if finding_data.evidence else []

    db_finding = Finding(
        job_id=finding_data.job_id,
        plugin_id=finding_data.plugin_id,
        stage=finding_data.stage,
        severity=finding_data.severity,
        category=finding_data.category,
        title=finding_data.title,
        description=finding_data.description,
        evidence=evidence_dicts,
        confidence=finding_data.confidence,
        tags=finding_data.tags
    )
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


def create_artifact(db: Session, artifact_data: Any) -> Artifact:
    db_artifact = Artifact(
        job_id=artifact_data.job_id,
        plugin_id=artifact_data.plugin_id,
        stage=artifact_data.stage,
        artifact_type=artifact_data.artifact_type,
        name=artifact_data.name,
        description=artifact_data.description,
        uri=artifact_data.uri,
        sha256=artifact_data.sha256,
        size_bytes=artifact_data.size_bytes,
        meta=artifact_data.meta
    )
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    return db_artifact


def create_trace_event(db: Session, event_data: Any) -> TraceEvent:
    db_event = TraceEvent(
        job_id=event_data.job_id,
        ts=event_data.ts,
        source=event_data.source,
        event_type=event_data.event_type,
        symbol=event_data.symbol,
        address=event_data.address,
        thread_id=event_data.thread_id,
        sequence=event_data.sequence,
        payload=event_data.payload
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
