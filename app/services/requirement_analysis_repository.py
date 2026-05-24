from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from app.storage.db import session_scope
from app.storage.db_models import (
    ProjectAttachmentRecord,
    RequirementAnalysisRecord,
    RequirementPendingItemRecord,
    RequirementRiskRecord,
    RequirementScenarioRecord,
)


class RequirementAnalysisRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self.session_factory = session_factory

    def load(self, project_id: str) -> dict[str, Any] | None:
        with session_scope(self.session_factory) as session:
            master = session.get(RequirementAnalysisRecord, project_id)
            if master is None:
                return None

            scenarios = (
                session.query(RequirementScenarioRecord)
                .filter(RequirementScenarioRecord.project_id == project_id)
                .order_by(RequirementScenarioRecord.sort_order, RequirementScenarioRecord.id)
                .all()
            )
            risks = (
                session.query(RequirementRiskRecord)
                .filter(RequirementRiskRecord.project_id == project_id)
                .order_by(RequirementRiskRecord.sort_order, RequirementRiskRecord.id)
                .all()
            )
            pending_items = (
                session.query(RequirementPendingItemRecord)
                .filter(RequirementPendingItemRecord.project_id == project_id)
                .order_by(RequirementPendingItemRecord.sort_order, RequirementPendingItemRecord.id)
                .all()
            )
            attachments = (
                session.query(ProjectAttachmentRecord)
                .filter(ProjectAttachmentRecord.project_id == project_id)
                .order_by(ProjectAttachmentRecord.sort_order, ProjectAttachmentRecord.id)
                .all()
            )

            return {
                "basic": {
                    "projectName": master.project_name,
                    "projectSummary": master.project_summary,
                    "industry": master.basic_industry,
                    "projectType": master.project_type,
                    "keywords": master.keywords,
                },
                "core": {
                    "background": master.background,
                    "goal": master.goal,
                    "users": master.users,
                    "painPoints": master.pain_points,
                },
                "scenarios": [
                    {
                        "key": row.item_key,
                        "title": row.title,
                        "description": row.description,
                        "flow": row.flow,
                    }
                    for row in scenarios
                ],
                "functions": {
                    "functionDesc": dict(master.function_desc or {}),
                    "nonFunction": dict(master.non_function or {}),
                    "constraints": dict(master.constraints_json or {}),
                },
                "risks": [
                    {
                        "key": row.item_key,
                        "title": row.title,
                        "level": row.level,
                        "description": row.description,
                        "impact": row.impact,
                        "strategy": row.strategy,
                    }
                    for row in risks
                ],
                "pending": {
                    "unknownInfo": master.unknown_info,
                    "assumptions": master.assumptions,
                    "items": [
                        {
                            "title": row.title,
                            "text": row.text,
                            "checked": bool(row.checked),
                        }
                        for row in pending_items
                    ],
                },
                "attachments": [
                    {
                        "id": str(row.id),
                        "name": row.name,
                        "meta": row.meta,
                        "size": row.size,
                        "content_type": row.content_type,
                        "storage_path": row.storage_path,
                        "uploaded_at": row.uploaded_at.isoformat() if row.uploaded_at else None,
                    }
                    for row in attachments
                ],
                "supplement": {
                    "notes": master.supplement_notes,
                },
            }

    def save_full(self, project_id: str, analysis: dict[str, Any], user_id: str | None = None) -> None:
        now = datetime.now()
        with session_scope(self.session_factory) as session:
            master = session.get(RequirementAnalysisRecord, project_id)
            if master is None:
                master = RequirementAnalysisRecord(
                    project_id=project_id,
                    created_id=user_id,
                    update_id=user_id,
                    created_at=now,
                    updated_at=now,
                    project_name="",
                    project_summary="",
                    basic_industry="",
                    project_type="",
                    keywords="",
                    background="",
                    goal="",
                    users="",
                    pain_points="",
                    function_desc={},
                    non_function={},
                    constraints_json={},
                    unknown_info="",
                    assumptions="",
                    supplement_notes="",
                )
                session.add(master)

            basic = dict(analysis.get("basic") or {})
            core = dict(analysis.get("core") or {})
            functions = dict(analysis.get("functions") or {})
            pending = dict(analysis.get("pending") or {})
            supplement = dict(analysis.get("supplement") or {})

            master.project_name = str(basic.get("projectName") or "")
            master.project_summary = str(basic.get("projectSummary") or "")
            master.basic_industry = str(basic.get("industry") or "")
            master.project_type = str(basic.get("projectType") or "")
            master.keywords = str(basic.get("keywords") or "")

            master.background = str(core.get("background") or "")
            master.goal = str(core.get("goal") or "")
            master.users = str(core.get("users") or "")
            master.pain_points = str(core.get("painPoints") or "")

            master.function_desc = dict(functions.get("functionDesc") or {})
            master.non_function = dict(functions.get("nonFunction") or {})
            master.constraints_json = dict(functions.get("constraints") or {})

            master.unknown_info = str(pending.get("unknownInfo") or "")
            master.assumptions = str(pending.get("assumptions") or "")

            master.supplement_notes = str(supplement.get("notes") or "")
            master.update_id = user_id
            master.updated_at = now

            session.query(RequirementScenarioRecord).filter(RequirementScenarioRecord.project_id == project_id).delete()
            session.query(RequirementRiskRecord).filter(RequirementRiskRecord.project_id == project_id).delete()
            session.query(RequirementPendingItemRecord).filter(RequirementPendingItemRecord.project_id == project_id).delete()
            session.query(ProjectAttachmentRecord).filter(ProjectAttachmentRecord.project_id == project_id).delete()

            for index, item in enumerate(list(analysis.get("scenarios") or [])):
                session.add(
                    RequirementScenarioRecord(
                        project_id=project_id,
                        sort_order=index,
                        created_id=user_id,
                        update_id=user_id,
                        item_key=str(item.get("key") or ""),
                        title=str(item.get("title") or ""),
                        description=str(item.get("description") or ""),
                        flow=str(item.get("flow") or ""),
                    )
                )

            for index, item in enumerate(list(analysis.get("risks") or [])):
                session.add(
                    RequirementRiskRecord(
                        project_id=project_id,
                        sort_order=index,
                        created_id=user_id,
                        update_id=user_id,
                        item_key=str(item.get("key") or ""),
                        title=str(item.get("title") or ""),
                        level=str(item.get("level") or "中"),
                        description=str(item.get("description") or ""),
                        impact=str(item.get("impact") or ""),
                        strategy=str(item.get("strategy") or ""),
                    )
                )

            for index, item in enumerate(list(pending.get("items") or [])):
                session.add(
                    RequirementPendingItemRecord(
                        project_id=project_id,
                        sort_order=index,
                        created_id=user_id,
                        update_id=user_id,
                        title=str(item.get("title") or ""),
                        text=str(item.get("text") or ""),
                        checked=bool(item.get("checked")),
                    )
                )

            for index, item in enumerate(list(analysis.get("attachments") or [])):
                session.add(
                    ProjectAttachmentRecord(
                        project_id=project_id,
                        sort_order=index,
                        created_id=user_id,
                        update_id=user_id,
                        name=str(item.get("name") or ""),
                        meta=str(item.get("meta") or ""),
                        size=item.get("size"),
                        content_type=str(item.get("content_type") or "") or None,
                        storage_path=str(item.get("storage_path") or "") or None,
                        uploaded_at=datetime.fromisoformat(str(item.get("uploaded_at"))) if item.get("uploaded_at") else None,
                    )
                )

    def save_partial(self, project_id: str, patch: dict[str, Any], default_analysis: dict[str, Any], user_id: str | None = None) -> dict[str, Any]:
        current = self.load(project_id) or default_analysis
        merged = self._merge(current, patch)
        self.save_full(project_id, merged, user_id=user_id)
        return merged

    def _merge(self, current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
        merged = dict(current)

        if patch.get("basic"):
            merged["basic"] = {**dict(current.get("basic") or {}), **dict(patch.get("basic") or {})}
        if patch.get("core"):
            merged["core"] = {**dict(current.get("core") or {}), **dict(patch.get("core") or {})}

        if patch.get("scenarios") is not None:
            merged["scenarios"] = list(patch.get("scenarios") or [])

        if patch.get("functions"):
            existing_functions = dict(current.get("functions") or {})
            incoming = dict(patch.get("functions") or {})
            functions = dict(existing_functions)
            for group_key in ("functionDesc", "nonFunction", "constraints"):
                value = incoming.get(group_key)
                if value is not None:
                    functions[group_key] = {
                        **dict(existing_functions.get(group_key) or {}),
                        **dict(value),
                    }
            merged["functions"] = functions

        if patch.get("risks") is not None:
            merged["risks"] = list(patch.get("risks") or [])

        if patch.get("pending"):
            pending_patch = dict(patch.get("pending") or {})
            existing_pending = dict(current.get("pending") or {})
            if "items" in pending_patch:
                merged["pending"] = {
                    **existing_pending,
                    **{k: v for k, v in pending_patch.items() if k != "items"},
                    "items": list(pending_patch.get("items") or []),
                }
            else:
                merged["pending"] = {**existing_pending, **pending_patch}

        if patch.get("attachments") is not None:
            merged["attachments"] = list(patch.get("attachments") or [])

        if patch.get("supplement"):
            merged["supplement"] = {**dict(current.get("supplement") or {}), **dict(patch.get("supplement") or {})}

        return merged
