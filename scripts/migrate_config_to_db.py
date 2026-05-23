from __future__ import annotations

from pathlib import Path

from app.services.requirement_analysis_repository import RequirementAnalysisRepository
from app.services.project_service import ProjectService
from app.storage.db import build_engine, build_session_factory
from app.storage.db_models import Base
from app.storage.header_store import build_header_store


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    engine = build_engine(base_dir)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)
    header_store = build_header_store(session_factory)
    project_service = ProjectService(base_dir, header_store=header_store)
    repository = RequirementAnalysisRepository(session_factory)

    migrated = 0
    for project in project_service.list_projects():
        config = dict(project.config or {})
        requirement_analysis = dict(config.get("requirementAnalysis") or {})
        if not requirement_analysis:
            requirement_analysis = project_service._create_default_requirement_analysis()

        repository.save_full(project.project_id, requirement_analysis)
        header_store.upsert_project(project)
        migrated += 1

    print(f"migrated projects: {migrated}")


if __name__ == "__main__":
    main()
