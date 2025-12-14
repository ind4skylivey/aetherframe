"""SQLAlchemy models for jobs, plugins, findings, and artifacts."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum, Float, Text
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Severity(str, enum.Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Plugin(Base):
    __tablename__ = "plugins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    version = Column(String(32), nullable=False, default="0.1.0")
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    jobs = relationship("Job", back_populates="plugin")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(256), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.pending, nullable=False)
    result = Column(JSON, nullable=True)
    pipeline_id = Column(String(64), nullable=True, default="quicklook")
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    plugin_id = Column(Integer, ForeignKey("plugins.id"), nullable=True)
    plugin = relationship("Plugin", back_populates="jobs")

    # Relationships to new entities
    findings = relationship("Finding", back_populates="job", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="job", cascade="all, delete-orphan")
    trace_events = relationship("TraceEvent", back_populates="job", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    job = relationship("Job")


class Finding(Base):
    """Finding from plugin analysis — normalized for querying."""
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    plugin_id = Column(String(64), nullable=True)
    stage = Column(String(64), nullable=True)

    severity = Column(Enum(Severity), default=Severity.info, nullable=False, index=True)
    category = Column(String(64), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)

    evidence = Column(JSON, nullable=True)  # List of evidence dicts
    confidence = Column(Float, default=1.0)
    tags = Column(JSON, nullable=True)  # List of strings

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="findings")


class Artifact(Base):
    """Artifact produced by plugin — reference to stored file."""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    plugin_id = Column(String(64), nullable=True)
    stage = Column(String(64), nullable=True)

    artifact_type = Column(String(32), nullable=False)  # json, html, dump, etc.
    name = Column(String(256), nullable=False)
    description = Column(String(512), nullable=True)
    uri = Column(String(1024), nullable=False)  # s3:// or file://
    sha256 = Column(String(64), nullable=True)
    size_bytes = Column(Integer, nullable=True)
    meta = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="artifacts")


class TraceEvent(Base):
    """Runtime trace event from dynamic analysis."""
    __tablename__ = "trace_events"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(String(64), nullable=False)  # laintrace, mnemosyne, etc.
    event_type = Column(String(64), nullable=False)  # hook_enter, state_change, etc.
    symbol = Column(String(256), nullable=True)
    address = Column(String(32), nullable=True)
    thread_id = Column(Integer, nullable=True)
    sequence = Column(Integer, nullable=True)
    payload = Column(JSON, nullable=True)

    job = relationship("Job", back_populates="trace_events")

