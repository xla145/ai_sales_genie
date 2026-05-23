from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


class PhaseId(str, Enum):
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"


class ProjectRun(BaseModel):
    run_id: str
    project_id: str
    session_id: str
    created_id: str | None = None
    update_id: str | None = None
    phase_id: PhaseId
    phase_name: str
    skill_name: str
    input_files: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    status: RunStatus = RunStatus.PENDING
    started_at: datetime
    ended_at: datetime | None = None
    error_message: str | None = None
    result_summary: dict[str, Any] | None = None
    log_path: str
    output_path: str | None = None
    result_summary_path: str | None = None
    detail_path: str | None = None


class SubtaskRun(BaseModel):
    subtask_id: str
    workflow_id: str
    project_id: str
    session_id: str
    phase_id: PhaseId
    phase_name: str
    skill_name: str
    title: str
    prompt: str
    input_files: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    status: RunStatus = RunStatus.PENDING
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_message: str | None = None
    result_summary: dict[str, Any] | None = None
    log_path: str
    order: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class WorkflowPhaseState(BaseModel):
    phase_id: PhaseId
    phase_name: str
    skill_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    input_files: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    subtask_ids: list[str] = Field(default_factory=list)
    result_summary: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class WorkflowRun(BaseModel):
    workflow_id: str
    project_id: str
    session_id: str
    created_id: str | None = None
    update_id: str | None = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    phases: list[WorkflowPhaseState] = Field(default_factory=list)
    current_phase_id: PhaseId | None = None
    created_at: datetime
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error_message: str | None = None
    result_summary: dict[str, Any] | None = None
    log_path: str
    detail_path: str | None = None
    session_snapshot: dict[str, Any] | None = None


class CreateRunRequest(BaseModel):
    session_id: str | None = None
    phase_id: PhaseId
    phase_name: str
    skill_name: str
    input_files: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    prompt: str | None = None
    fail: bool = False
    sleep_seconds: float = Field(default=0.0, ge=0.0, le=30.0)


class CreateWorkflowRequest(BaseModel):
    session_id: str | None = None
    prompt: str | None = None
    max_parallel_subagents: int = Field(default=2, ge=1, le=4)
    fail: bool = False
    sleep_seconds: float = Field(default=0.0, ge=0.0, le=30.0)
