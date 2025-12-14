"""Pydantic schemas."""

from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict
from .models import JobStatus


class PluginCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    version: str = Field(default="0.1.0", max_length=32)
    description: Optional[str] = Field(default=None, max_length=512)


class PluginRead(PluginCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobCreate(BaseModel):
    target: str = Field(min_length=1, max_length=256)
    plugin_id: Optional[int] = None
    pipeline_id: Optional[str] = Field(default="quicklook", max_length=64)


class JobRead(BaseModel):
    id: int
    target: str
    status: JobStatus
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    plugin_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class EventCreate(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    job_id: Optional[int] = None


class EventRead(BaseModel):
    id: int
    event_type: str
    payload: Dict[str, Any]
    created_at: datetime
    job_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

