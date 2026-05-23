"""init schema

Revision ID: 1f98159021b9
Revises: 
Create Date: 2026-05-23 11:52:35.274306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f98159021b9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "projects",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(length=1024), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_project_id"), "projects", ["project_id"], unique=True)

    op.create_table(
        "project_sessions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("hermes_session_id", sa.String(length=128), nullable=True),
        sa.Column("memory_md", sa.Text(), nullable=True),
        sa.Column("project_index", sa.JSON(), nullable=True),
        sa.Column("message_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_sessions_project_id"), "project_sessions", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_sessions_session_id"), "project_sessions", ["session_id"], unique=True)

    op.create_table(
        "project_runs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("run_type", sa.String(length=32), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("current_step", sa.String(length=255), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("input_snapshot_path", sa.String(length=1024), nullable=True),
        sa.Column("output_snapshot_path", sa.String(length=1024), nullable=True),
        sa.Column("patch_path", sa.String(length=1024), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_project_runs_project_id"), "project_runs", ["project_id"], unique=False)
    op.create_index(op.f("ix_project_runs_run_id"), "project_runs", ["run_id"], unique=True)
    op.create_index(op.f("ix_project_runs_session_id"), "project_runs", ["session_id"], unique=False)
    op.create_index(op.f("ix_project_runs_status"), "project_runs", ["status"], unique=False)

    op.create_table(
        "requirements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("requirement_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=True),
        sa.Column("parent_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requirement_type", sa.String(length=32), nullable=True),
        sa.Column("priority", sa.String(length=32), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("acceptance_criteria", sa.JSON(), nullable=True),
        sa.Column("estimated_complexity", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requirements_parent_id"), "requirements", ["parent_id"], unique=False)
    op.create_index(op.f("ix_requirements_project_id"), "requirements", ["project_id"], unique=False)
    op.create_index(op.f("ix_requirements_requirement_id"), "requirements", ["requirement_id"], unique=True)
    op.create_index(op.f("ix_requirements_run_id"), "requirements", ["run_id"], unique=False)

    op.create_table(
        "run_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("message_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_messages_message_id"), "run_messages", ["message_id"], unique=True)
    op.create_index(op.f("ix_run_messages_project_id"), "run_messages", ["project_id"], unique=False)
    op.create_index(op.f("ix_run_messages_run_id"), "run_messages", ["run_id"], unique=False)

    op.create_table(
        "run_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_run_events_event_id"), "run_events", ["event_id"], unique=True)
    op.create_index(op.f("ix_run_events_project_id"), "run_events", ["project_id"], unique=False)
    op.create_index(op.f("ix_run_events_run_id"), "run_events", ["run_id"], unique=False)

    op.create_table(
        "tool_calls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("tool_call_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=True),
        sa.Column("output_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tool_calls_project_id"), "tool_calls", ["project_id"], unique=False)
    op.create_index(op.f("ix_tool_calls_run_id"), "tool_calls", ["run_id"], unique=False)
    op.create_index(op.f("ix_tool_calls_tool_call_id"), "tool_calls", ["tool_call_id"], unique=True)
    op.create_index(op.f("ix_tool_calls_tool_name"), "tool_calls", ["tool_name"], unique=False)

    op.create_table(
        "file_changes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("file_path", sa.String(length=1024), nullable=False),
        sa.Column("change_type", sa.String(length=32), nullable=False),
        sa.Column("old_hash", sa.String(length=128), nullable=True),
        sa.Column("new_hash", sa.String(length=128), nullable=True),
        sa.Column("diff_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_file_changes_file_path"), "file_changes", ["file_path"], unique=False, mysql_length=255)
    op.create_index(op.f("ix_file_changes_project_id"), "file_changes", ["project_id"], unique=False)
    op.create_index(op.f("ix_file_changes_run_id"), "file_changes", ["run_id"], unique=False)

    op.create_table(
        "artifacts",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("artifact_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("artifact_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("storage_url", sa.String(length=1024), nullable=True),
        sa.Column("storage_path", sa.String(length=1024), nullable=True),
        sa.Column("mime_type", sa.String(length=128), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("sha256", sa.String(length=128), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artifacts_artifact_id"), "artifacts", ["artifact_id"], unique=True)
    op.create_index(op.f("ix_artifacts_project_id"), "artifacts", ["project_id"], unique=False)
    op.create_index(op.f("ix_artifacts_run_id"), "artifacts", ["run_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_artifacts_run_id"), table_name="artifacts")
    op.drop_index(op.f("ix_artifacts_project_id"), table_name="artifacts")
    op.drop_index(op.f("ix_artifacts_artifact_id"), table_name="artifacts")
    op.drop_table("artifacts")

    op.drop_index(op.f("ix_file_changes_run_id"), table_name="file_changes")
    op.drop_index(op.f("ix_file_changes_project_id"), table_name="file_changes")
    op.drop_index(op.f("ix_file_changes_file_path"), table_name="file_changes")
    op.drop_table("file_changes")

    op.drop_index(op.f("ix_tool_calls_tool_name"), table_name="tool_calls")
    op.drop_index(op.f("ix_tool_calls_tool_call_id"), table_name="tool_calls")
    op.drop_index(op.f("ix_tool_calls_run_id"), table_name="tool_calls")
    op.drop_index(op.f("ix_tool_calls_project_id"), table_name="tool_calls")
    op.drop_table("tool_calls")

    op.drop_index(op.f("ix_run_events_run_id"), table_name="run_events")
    op.drop_index(op.f("ix_run_events_project_id"), table_name="run_events")
    op.drop_index(op.f("ix_run_events_event_id"), table_name="run_events")
    op.drop_table("run_events")

    op.drop_index(op.f("ix_run_messages_run_id"), table_name="run_messages")
    op.drop_index(op.f("ix_run_messages_project_id"), table_name="run_messages")
    op.drop_index(op.f("ix_run_messages_message_id"), table_name="run_messages")
    op.drop_table("run_messages")

    op.drop_index(op.f("ix_requirements_run_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_requirement_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_project_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_parent_id"), table_name="requirements")
    op.drop_table("requirements")

    op.drop_index(op.f("ix_project_runs_status"), table_name="project_runs")
    op.drop_index(op.f("ix_project_runs_session_id"), table_name="project_runs")
    op.drop_index(op.f("ix_project_runs_run_id"), table_name="project_runs")
    op.drop_index(op.f("ix_project_runs_project_id"), table_name="project_runs")
    op.drop_table("project_runs")

    op.drop_index(op.f("ix_project_sessions_session_id"), table_name="project_sessions")
    op.drop_index(op.f("ix_project_sessions_project_id"), table_name="project_sessions")
    op.drop_table("project_sessions")

    op.drop_index(op.f("ix_projects_project_id"), table_name="projects")
    op.drop_table("projects")
