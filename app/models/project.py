from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ProjectOverviewPatch(BaseModel):
    name: str | None = None
    description: str | None = None
    clientInfo: str | None = None
    province: str | None = None
    city: str | None = None
    stage: str | None = None
    industry: str | None = None


class RequirementAnalysisPatch(BaseModel):
    basic: dict[str, Any] = Field(default_factory=dict)
    core: dict[str, Any] = Field(default_factory=dict)
    scenarios: list[dict[str, Any]] | None = None
    functions: dict[str, Any] = Field(default_factory=dict)
    risks: list[dict[str, Any]] | None = None
    pending: dict[str, Any] = Field(default_factory=dict)
    attachments: list[dict[str, Any]] | None = None
    supplement: dict[str, Any] = Field(default_factory=dict)


class ProjectStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"


class Project(BaseModel):
    project_id: str
    name: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.CREATED
    workspace_path: str
    current_session_id: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class UpdateProjectRequest(BaseModel):
    name: str
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)


class UpdateProjectOverviewRequest(ProjectOverviewPatch):
    pass


class UpdateRequirementAnalysisRequest(RequirementAnalysisPatch):
    pass


class RunPhase1Request(BaseModel):
    prompt: str
    session_id: str | None = None


class RunPhase1Response(BaseModel):
    project: Project
    run_id: str
    session_id: str
    status: str
    result_summary: dict[str, Any] | None = None
