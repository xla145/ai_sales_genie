from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.storage.db import Base


class UserRecord(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)


class ProjectRecord(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="created")
    workspace_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    current_session_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    client_info: Mapped[str | None] = mapped_column(String(255), nullable=True)
    province: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(64), nullable=True)
    stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    requirement_analysis: Mapped[RequirementAnalysisRecord | None] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        uselist=False,
    )
    requirement_scenarios: Mapped[list[RequirementScenarioRecord]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    requirement_risks: Mapped[list[RequirementRiskRecord]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    requirement_pending_items: Mapped[list[RequirementPendingItemRecord]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    project_attachments: Mapped[list[ProjectAttachmentRecord]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class RequirementAnalysisRecord(Base):
    __tablename__ = "requirement_analyses"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), primary_key=True)

    project_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    project_summary: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    basic_industry: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    project_type: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    keywords: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    background: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    goal: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    users: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    pain_points: Mapped[str] = mapped_column(Text(), nullable=False, default="")

    function_desc: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    non_function: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    constraints_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    unknown_info: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    assumptions: Mapped[str] = mapped_column(Text(), nullable=False, default="")

    supplement_notes: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)

    project: Mapped[ProjectRecord] = relationship(back_populates="requirement_analysis")


class RequirementScenarioRecord(Base):
    __tablename__ = "requirement_scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    item_key: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    flow: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)

    project: Mapped[ProjectRecord] = relationship(back_populates="requirement_scenarios")


class RequirementRiskRecord(Base):
    __tablename__ = "requirement_risks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    item_key: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    level: Mapped[str] = mapped_column(String(32), nullable=False, default="中")
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    impact: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    strategy: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)

    project: Mapped[ProjectRecord] = relationship(back_populates="requirement_risks")


class RequirementPendingItemRecord(Base):
    __tablename__ = "requirement_pending_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    text: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    checked: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)

    project: Mapped[ProjectRecord] = relationship(back_populates="requirement_pending_items")


class ProjectAttachmentRecord(Base):
    __tablename__ = "project_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id", ondelete="CASCADE"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    meta: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    storage_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)

    project: Mapped[ProjectRecord] = relationship(back_populates="project_attachments")


class ProjectSessionRecord(Base):
    __tablename__ = "project_sessions"

    session_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    workspace_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    conversation: Mapped[str] = mapped_column(String(255), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    llm_provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_session_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    hermes_session_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)


class ProjectRunRecord(Base):
    __tablename__ = "project_runs"

    run_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    phase_id: Mapped[str] = mapped_column(String(32), nullable=False)
    phase_name: Mapped[str] = mapped_column(String(255), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    log_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    output_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    result_summary_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    detail_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)


class WorkflowRecord(Base):
    __tablename__ = "workflows"

    workflow_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    current_phase_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    update_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    log_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    detail_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
