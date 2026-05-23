from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TypedDict

from fastapi import Request
from dotenv import load_dotenv

from app.runtime_core.config import EngineConfig
from app.runtime_core.llm.provider_factory import create_llm_client_from_engine_config
from app.services.orchestrator_service import WorkflowService
from app.services.project_service import ProjectService
from app.services.run_service import RunService
from app.services.session_service import SessionService
from app.storage.db import build_engine, build_session_factory
from app.storage.db_models import Base
from app.storage.header_store import build_header_store


class ServiceContainer(TypedDict):
    project_service: ProjectService
    session_service: SessionService
    run_service: RunService
    workflow_service: WorkflowService


@lru_cache(maxsize=1)
def build_service_container() -> ServiceContainer:
    base_dir = Path(__file__).resolve().parent.parent.parent
    load_dotenv(base_dir / ".env")

    engine = build_engine(base_dir)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)
    header_store = build_header_store(session_factory)
    project_service = ProjectService(base_dir, header_store=header_store)
    session_service = SessionService(header_store=header_store)
    engine_config = EngineConfig.from_env()
    llm_client = create_llm_client_from_engine_config(engine_config)
    run_service = RunService(base_dir, project_service, session_service, llm_client, header_store=header_store)
    workflow_service = WorkflowService(base_dir, project_service, session_service, llm_client, header_store=header_store)
    return {
        "project_service": project_service,
        "session_service": session_service,
        "run_service": run_service,
        "workflow_service": workflow_service,
    }


def get_project_service(request: Request | None = None) -> ProjectService:
    if request is not None and hasattr(request.app.state, "services"):
        return request.app.state.services["project_service"]
    return build_service_container()["project_service"]


def get_session_service(request: Request | None = None) -> SessionService:
    if request is not None and hasattr(request.app.state, "services"):
        return request.app.state.services["session_service"]
    return build_service_container()["session_service"]


def get_run_service(request: Request | None = None) -> RunService:
    if request is not None and hasattr(request.app.state, "services"):
        return request.app.state.services["run_service"]
    return build_service_container()["run_service"]


def get_workflow_service(request: Request | None = None) -> WorkflowService:
    if request is not None and hasattr(request.app.state, "services"):
        return request.app.state.services["workflow_service"]
    return build_service_container()["workflow_service"]
