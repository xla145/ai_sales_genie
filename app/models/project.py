from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RequirementBasicItem(BaseModel):
    projectName: str = ""
    projectSummary: str = ""
    industry: str = ""
    projectType: str = ""
    keywords: str = ""


class RequirementCoreItem(BaseModel):
    background: str = ""
    goal: str = ""
    users: str = ""
    painPoints: str = ""


class RequirementScenarioItem(BaseModel):
    key: str = ""
    title: str = ""
    description: str = ""
    flow: str = ""


class RequirementFunctions(BaseModel):
    functionDesc: dict[str, str] = Field(default_factory=dict)
    nonFunction: dict[str, str] = Field(default_factory=dict)
    constraints: dict[str, str] = Field(default_factory=dict)


class RequirementRiskItem(BaseModel):
    key: str = ""
    title: str = ""
    level: str = "中"
    description: str = ""
    impact: str = ""
    strategy: str = ""


class RequirementPendingItem(BaseModel):
    title: str = ""
    text: str = ""
    checked: bool = False


class RequirementPending(BaseModel):
    unknownInfo: str = ""
    assumptions: str = ""
    items: list[RequirementPendingItem] = Field(default_factory=list)


class RequirementAttachmentItem(BaseModel):
    id: str | None = None
    name: str = ""
    meta: str = ""
    size: int | None = None
    content_type: str | None = None
    storage_path: str | None = None
    uploaded_at: datetime | None = None


class RequirementSupplement(BaseModel):
    notes: str = ""


class RequirementAnalysis(BaseModel):
    basic: RequirementBasicItem = Field(default_factory=RequirementBasicItem)
    core: RequirementCoreItem = Field(default_factory=RequirementCoreItem)
    scenarios: list[RequirementScenarioItem] = Field(default_factory=list)
    functions: RequirementFunctions = Field(default_factory=RequirementFunctions)
    risks: list[RequirementRiskItem] = Field(default_factory=list)
    pending: RequirementPending = Field(default_factory=RequirementPending)
    attachments: list[RequirementAttachmentItem] = Field(default_factory=list)
    supplement: RequirementSupplement = Field(default_factory=RequirementSupplement)


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
    created_id: str | None = None
    update_id: str | None = None
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
