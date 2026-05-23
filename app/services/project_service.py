from __future__ import annotations

from functools import lru_cache
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
import re
import shutil
from uuid import uuid4

from app.models.project import (
    CreateProjectRequest,
    Project,
    ProjectStatus,
    UpdateProjectOverviewRequest,
    UpdateProjectRequest,
    UpdateRequirementAnalysisRequest,
)
from app.services.requirement_analysis_repository import RequirementAnalysisRepository
from app.storage.file_store import FileStore
from app.storage.header_paths import project_config_path, project_file_path
from app.storage.header_store import HeaderStore


class ProjectService:
    MAX_REQUIREMENT_UPLOAD_BYTES = 20 * 1024 * 1024
    REQUIREMENT_UPLOAD_EXTENSIONS = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".png", ".jpg", ".jpeg"}

    def __init__(self, base_dir: Path, header_store: HeaderStore | None = None) -> None:
        self.base_dir = base_dir
        self.projects_dir = self.base_dir / "data" / "projects"
        self.store = FileStore()
        self.header_store = header_store
        self.requirement_repo = self._build_requirement_repo(header_store)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, payload: CreateProjectRequest, user_id: str) -> Project:
        now = datetime.now()
        project_id = f"proj_{uuid4().hex[:8]}"
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=False)

        config = dict(payload.config or {})
        config = self._normalize_config(config)

        project = Project(
            project_id=project_id,
            created_id=user_id,
            update_id=user_id,
            name=payload.name,
            description=payload.description,
            status=ProjectStatus.CREATED,
            workspace_path=str(project_dir),
            config=config,
            created_at=now,
            updated_at=now,
        )
        self.store.write_json(project_file_path(project), project.model_dump(mode="json"))
        self.store.write_json(project_config_path(project), config)
        if self.header_store is not None:
            self.header_store.upsert_project(project)
        if self.requirement_repo is not None:
            self.requirement_repo.save_full(project_id, config["requirementAnalysis"], user_id=user_id)
        return project

    def get_project(self, project_id: str) -> Project:
        project_path = self.projects_dir / project_id / "project.json"
        data = self.store.read_json(project_path)
        if not data:
            raise FileNotFoundError(project_id)
        project = Project.model_validate(data)
        return self._hydrate_project_config(project)

    def get_project_for_user(self, project_id: str, user_id: str) -> Project:
        if self.header_store is not None:
            project = self.header_store.get_project(project_id, user_id)
            if project is None:
                raise FileNotFoundError(project_id)
            return self._hydrate_project_config(project)

        project = self.get_project(project_id)
        if project.created_id is None:
            project.created_id = user_id
            if project.update_id is None:
                project.update_id = user_id
            self.save_project(project, user_id=user_id)
            return project
        if project.created_id != user_id:
            raise FileNotFoundError(project_id)
        return project

    def list_projects_for_user(self, user_id: str) -> list[Project]:
        if self.header_store is not None:
            return [self._hydrate_project_config(project) for project in self.header_store.list_projects(user_id)]

        projects: list[Project] = []
        for project_file in sorted(self.projects_dir.glob("*/project.json")):
            data = self.store.read_json(project_file)
            if data:
                project = self._hydrate_project_config(Project.model_validate(data))
                if project.created_id is None:
                    project.created_id = user_id
                    if project.update_id is None:
                        project.update_id = user_id
                    self.save_project(project, user_id=user_id)
                    projects.append(project)
                elif project.created_id == user_id:
                    projects.append(project)
        return projects

    def save_project(self, project: Project, user_id: str | None = None) -> None:
        if user_id is not None:
            project.update_id = user_id
        project.updated_at = datetime.now()
        project.config = self._normalize_config(dict(project.config or {}))
        self.store.write_json(project_file_path(project), project.model_dump(mode="json"))
        self.store.write_json(project_config_path(project), project.config)
        if self.header_store is not None:
            self.header_store.upsert_project(project)
        if self.requirement_repo is not None:
            self.requirement_repo.save_full(project.project_id, project.config["requirementAnalysis"], user_id=user_id)

    def update_project(self, project_id: str, payload: UpdateProjectRequest, user_id: str) -> Project:
        project = self.get_project_for_user(project_id, user_id)
        project.name = payload.name
        project.description = payload.description
        project.config = self._normalize_config(dict(payload.config or {}))
        self.save_project(project, user_id=user_id)
        return project

    def update_project_overview(self, project_id: str, payload: UpdateProjectOverviewRequest, user_id: str) -> Project:
        project = self.get_project_for_user(project_id, user_id)
        if payload.name is not None:
            project.name = payload.name
        if payload.description is not None:
            project.description = payload.description

        config = self._normalize_config(dict(project.config or {}))
        for key in ("clientInfo", "province", "city", "stage", "industry"):
            value = getattr(payload, key)
            if value is not None:
                config[key] = value

        project.config = config
        self.save_project(project, user_id=user_id)
        return project

    def update_requirement_analysis(self, project_id: str, payload: UpdateRequirementAnalysisRequest, user_id: str) -> Project:
        project = self.get_project_for_user(project_id, user_id)
        config = self._normalize_config(dict(project.config or {}))

        patch = payload.model_dump(exclude_none=True)
        if self.requirement_repo is not None:
            merged = self.requirement_repo.save_partial(project_id, patch, self._create_default_requirement_analysis(), user_id=user_id)
        else:
            merged = self._merge_requirement_analysis(config["requirementAnalysis"], patch)

        config["requirementAnalysis"] = merged
        project.config = config
        self.save_project(project, user_id=user_id)
        return project

    def list_requirement_uploads(self, project_id: str, user_id: str) -> list[dict]:
        project = self.get_project_for_user(project_id, user_id)
        analysis = self._normalize_config(dict(project.config or {}))["requirementAnalysis"]
        return list(analysis.get("attachments") or [])

    def upload_requirement_file(self, project_id: str, user_id: str, *, filename: str, content_type: str | None, file_obj: BinaryIO) -> dict:
        project = self.get_project_for_user(project_id, user_id)
        original_name = Path(filename or "upload").name
        extension = Path(original_name).suffix.lower()
        if extension not in self.REQUIREMENT_UPLOAD_EXTENSIONS:
            raise ValueError("Unsupported requirement file type")

        upload_dir = self._requirement_upload_dir(project)
        upload_dir.mkdir(parents=True, exist_ok=True)
        upload_id = f"upload_{uuid4().hex[:12]}"
        stored_name = f"{upload_id}{extension}"
        storage_path = upload_dir / stored_name
        size = self._write_limited_upload(file_obj, storage_path)
        uploaded_at = datetime.now()
        attachment = {
            "id": upload_id,
            "name": original_name,
            "meta": self._format_upload_meta(size, uploaded_at),
            "size": size,
            "content_type": content_type,
            "storage_path": str(storage_path.relative_to(Path(project.workspace_path))),
            "uploaded_at": uploaded_at.isoformat(),
        }

        config = self._normalize_config(dict(project.config or {}))
        analysis = dict(config["requirementAnalysis"])
        attachments = [attachment, *list(analysis.get("attachments") or [])]
        analysis["attachments"] = attachments
        config["requirementAnalysis"] = analysis
        project.config = config
        self.save_project(project, user_id=user_id)
        return attachment

    def delete_requirement_upload(self, project_id: str, user_id: str, upload_id: str) -> None:
        project = self.get_project_for_user(project_id, user_id)
        config = self._normalize_config(dict(project.config or {}))
        analysis = dict(config["requirementAnalysis"])
        attachments = list(analysis.get("attachments") or [])
        target = next((item for item in attachments if str(item.get("id") or "") == upload_id), None)
        if target is None:
            raise FileNotFoundError(upload_id)

        storage_path = str(target.get("storage_path") or "")
        if storage_path:
            candidate = (Path(project.workspace_path) / storage_path).resolve()
            upload_root = self._requirement_upload_dir(project).resolve()
            if candidate == upload_root or upload_root in candidate.parents:
                candidate.unlink(missing_ok=True)

        analysis["attachments"] = [item for item in attachments if str(item.get("id") or "") != upload_id]
        config["requirementAnalysis"] = analysis
        project.config = config
        self.save_project(project, user_id=user_id)

    def read_phase1_requirement_doc(self, project_id: str, user_id: str) -> str:
        project = self.get_project_for_user(project_id, user_id)
        target = Path(project.workspace_path) / "需求结构化.md"
        if not target.exists():
            raise FileNotFoundError(target.name)
        return target.read_text(encoding="utf-8")

    def build_requirement_analysis_from_phase1(self, project_id: str, user_id: str) -> dict:
        content = self.read_phase1_requirement_doc(project_id, user_id)
        project = self.get_project_for_user(project_id, user_id)
        existing = dict((project.config or {}).get("requirementAnalysis") or {})
        defaults = self._create_default_requirement_analysis()

        basic_info = self._parse_named_table(content, "## 2. 项目基础信息")
        background = self._parse_named_table(content, "### 3.1 项目背景")
        goals = self._parse_named_table(content, "### 3.2 项目目标")
        users = self._parse_core_users(content)
        pain_points = self._parse_pain_points(content)
        scenarios = self._parse_scenarios(content)
        explicit_functions = self._parse_markdown_table_rows(content, "### 5.1 显性功能点")
        latent_functions = self._parse_markdown_table_rows(content, "### 5.2 潜在功能点")
        tech_requirements = self._parse_named_table(content, "## 6. 技术需求")
        non_function_requirements = self._parse_named_table(content, "## 7. 非功能需求")
        constraints = self._parse_named_table(content, "## 8. 约束条件")
        risks = self._parse_risks(content)
        pending_unknown_items = self._parse_pending_unknown_items(content)
        assumptions = self._parse_assumptions(content)

        pending_unknown_summary = "\n".join(item["text"] for item in pending_unknown_items)
        assumption_summary = "\n".join(
            f"{item['title']}：{item['text']}" if item["title"] else item["text"]
            for item in assumptions
        )

        existing_basic = dict(existing.get("basic") or {})
        existing_core = dict(existing.get("core") or {})
        existing_functions = dict(existing.get("functions") or {})
        existing_pending = dict(existing.get("pending") or {})
        existing_supplement = dict(existing.get("supplement") or {})

        return {
            **defaults,
            **existing,
            "basic": {
                **defaults["basic"],
                **existing_basic,
                "projectName": basic_info.get("项目名称", existing_basic.get("projectName", "")),
                "projectSummary": basic_info.get("项目摘要", existing_basic.get("projectSummary", "")),
                "industry": basic_info.get("对应行业", existing_basic.get("industry", "")),
                "projectType": basic_info.get("项目类型", existing_basic.get("projectType", "")),
                "keywords": basic_info.get("项目关键词", existing_basic.get("keywords", "")),
            },
            "core": {
                **defaults["core"],
                **existing_core,
                "background": "\n".join(filter(None, [
                    background.get("项目背景", ""),
                    background.get("立项原因", ""),
                    background.get("当前现状", ""),
                ])).strip(),
                "goal": "\n".join(filter(None, [
                    goals.get("业务目标（显性）", ""),
                    goals.get("用户目标（隐性）", ""),
                    goals.get("成功指标", ""),
                ])).strip(),
                "users": users or existing_core.get("users", ""),
                "painPoints": pain_points or existing_core.get("painPoints", ""),
            },
            "scenarios": scenarios or existing.get("scenarios") or defaults["scenarios"],
            "functions": {
                "functionDesc": {
                    **defaults["functions"]["functionDesc"],
                    **dict(existing_functions.get("functionDesc") or {}),
                    "显性核心功能点": explicit_functions,
                    "潜在功能点": latent_functions,
                    "技术选型": tech_requirements.get("技术选型", ""),
                    "技术架构": tech_requirements.get("技术架构", ""),
                    "依赖系统": tech_requirements.get("依赖系统", ""),
                },
                "nonFunction": {
                    **defaults["functions"]["nonFunction"],
                    **dict(existing_functions.get("nonFunction") or {}),
                    "性能要求": non_function_requirements.get("性能要求", ""),
                    "可用性要求": non_function_requirements.get("可用性要求", ""),
                    "安全性要求": non_function_requirements.get("安全性要求", ""),
                    "兼容性要求": non_function_requirements.get("兼容性要求", ""),
                },
                "constraints": {
                    **defaults["functions"]["constraints"],
                    **dict(existing_functions.get("constraints") or {}),
                    "性能约束": constraints.get("性能约束", ""),
                    "可用性约束": constraints.get("可用性约束", ""),
                    "安全性约束": constraints.get("安全性约束", ""),
                    "兼容性约束": constraints.get("兼容性约束", ""),
                },
            },
            "risks": risks or existing.get("risks") or defaults["risks"],
            "pending": {
                **defaults["pending"],
                **existing_pending,
                "unknownInfo": pending_unknown_summary or existing_pending.get("unknownInfo", ""),
                "assumptions": assumption_summary or existing_pending.get("assumptions", ""),
                "items": pending_unknown_items or existing_pending.get("items") or defaults["pending"]["items"],
            },
            "attachments": existing.get("attachments") or [],
            "supplement": {
                **defaults["supplement"],
                **existing_supplement,
                "notes": existing_supplement.get("notes", ""),
            },
        }

    def sync_requirement_analysis_from_phase1(self, project_id: str, user_id: str) -> Project:
        project = self.get_project_for_user(project_id, user_id)
        config = self._normalize_config(dict(project.config or {}))
        analysis = self.build_requirement_analysis_from_phase1(project_id, user_id)
        if self.requirement_repo is not None:
            self.requirement_repo.save_full(project_id, analysis, user_id=user_id)
        config["requirementAnalysis"] = analysis
        project.config = config
        self.save_project(project, user_id=user_id)
        return project

    @lru_cache(maxsize=1)
    def _create_default_requirement_analysis(self) -> dict:
        return {
            "basic": {
                "projectName": "",
                "projectSummary": "",
                "industry": "",
                "projectType": "",
                "keywords": "",
            },
            "core": {
                "background": "",
                "goal": "",
                "users": "",
                "painPoints": "",
            },
            "scenarios": [{"key": "scenario-1", "title": "场景1", "description": "", "flow": ""}],
            "functions": {
                "functionDesc": {
                    "显性核心功能点": "",
                    "潜在功能点": "",
                    "技术选型": "",
                    "技术架构": "",
                    "依赖系统": "",
                },
                "nonFunction": {
                    "性能要求": "",
                    "可用性要求": "",
                    "安全性要求": "",
                    "兼容性要求": "",
                },
                "constraints": {
                    "性能约束": "",
                    "可用性约束": "",
                    "安全性约束": "",
                    "兼容性约束": "",
                },
            },
            "risks": [{"key": "risk-1", "title": "风险点1", "level": "中", "description": "", "impact": "", "strategy": ""}],
            "pending": {
                "unknownInfo": "",
                "assumptions": "",
                "items": [
                    {"title": "待确认事项1", "text": "", "checked": False},
                ],
            },
            "attachments": [],
            "supplement": {
                "notes": "",
            },
        }

    def _write_limited_upload(self, file_obj: BinaryIO, storage_path: Path) -> int:
        size = 0
        with storage_path.open("wb") as target:
            while chunk := file_obj.read(1024 * 1024):
                size += len(chunk)
                if size > self.MAX_REQUIREMENT_UPLOAD_BYTES:
                    target.close()
                    storage_path.unlink(missing_ok=True)
                    raise ValueError("Requirement file is too large")
                target.write(chunk)
        return size

    def _requirement_upload_dir(self, project: Project) -> Path:
        return Path(project.workspace_path) / "requirements" / "uploads"

    def _format_upload_meta(self, size: int, uploaded_at: datetime) -> str:
        if size >= 1024 * 1024:
            display_size = f"{size / 1024 / 1024:.1f} MB"
        elif size >= 1024:
            display_size = f"{size / 1024:.1f} KB"
        else:
            display_size = f"{size} B"
        return f"{display_size} · {uploaded_at.strftime('%Y-%m-%d %H:%M')}"

    def _normalize_config(self, config: dict) -> dict:
        result = dict(config)
        result.setdefault("clientInfo", "")
        result.setdefault("province", "")
        result.setdefault("city", "")
        result.setdefault("stage", "")
        result.setdefault("industry", "")
        result["requirementAnalysis"] = self._merge_requirement_analysis(
            self._create_default_requirement_analysis(),
            dict(result.get("requirementAnalysis") or {}),
        )
        return result

    def _merge_requirement_analysis(self, current: dict, patch: dict) -> dict:
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

    def _build_requirement_repo(self, header_store: HeaderStore | None) -> RequirementAnalysisRepository | None:
        if header_store is None or not hasattr(header_store, "session_factory"):
            return None
        return RequirementAnalysisRepository(getattr(header_store, "session_factory"))

    def _extract_section(self, content: str, heading: str) -> str:
        start = content.find(heading)
        if start == -1:
            return ""
        next_heading = re.search(r"\n##\s+\d+\.|\n##\s+[^\n]+", content[start + len(heading):])
        if next_heading:
            end = start + len(heading) + next_heading.start()
            return content[start:end].strip()
        return content[start:].strip()

    def _extract_subsection(self, content: str, heading: str) -> str:
        start = content.find(heading)
        if start == -1:
            return ""
        next_heading = re.search(r"\n###\s+|\n##\s+", content[start + len(heading):])
        if next_heading:
            end = start + len(heading) + next_heading.start()
            return content[start:end].strip()
        return content[start:].strip()

    def _parse_markdown_table_rows(self, content: str, heading: str) -> str:
        section = self._extract_subsection(content, heading)
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return ""
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            meaningful = [cell for cell in cells if cell and cell != "---"]
            if meaningful:
                rows.append(" / ".join(meaningful))
        return "\n".join(rows)

    def _parse_named_table(self, content: str, heading: str) -> dict[str, str]:
        section = self._extract_subsection(content, heading)
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return {}
        result: dict[str, str] = {}
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] and cells[0] != "---":
                result[cells[0]] = cells[1]
        return result

    def _parse_core_users(self, content: str) -> str:
        section = self._extract_subsection(content, "### 3.3 核心用户")
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return ""
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 4 and any(cells[:4]):
                rows.append(" / ".join(cell for cell in cells[:4] if cell))
        return "\n".join(rows)

    def _parse_pain_points(self, content: str) -> str:
        section = self._extract_subsection(content, "### 3.4 当前痛点")
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return ""
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 3 and any(cells[:3]):
                rows.append(" / ".join(cell for cell in cells[:3] if cell))
        return "\n".join(rows)

    def _parse_scenarios(self, content: str) -> list[dict]:
        section = self._extract_section(content, "## 4. 场景与诉求分析")
        matches = re.findall(r"###\s+场景\s*(\d+)：(.*?)(?=\n###\s+场景\s*\d+：|\n##\s+5\.|\Z)", section, flags=re.S)
        scenarios: list[dict] = []
        for index, (_, block) in enumerate(matches, start=1):
            title_match = re.search(r"^(.*?)\n", block.strip())
            title = title_match.group(1).strip() if title_match else f"场景{index}"
            description = self._extract_bullet_value(block, "场景描述")
            flow = self._extract_numbered_block(block, "场景流程")
            scenarios.append({
                "key": f"scenario-{index}",
                "title": title or f"场景{index}",
                "description": description,
                "flow": flow,
            })
        return scenarios

    def _parse_risks(self, content: str) -> list[dict]:
        section = self._extract_section(content, "## 9. 风险点与关注点")
        matches = re.findall(r"###\s+风险点\s*(\d+)：(.*?)(?=\n###\s+风险点\s*\d+：|\n##\s+10\.|\Z)", section, flags=re.S)
        risks: list[dict] = []
        for index, (risk_index, block) in enumerate(matches, start=1):
            title = block.strip().splitlines()[0].strip() if block.strip().splitlines() else f"风险点{risk_index}"
            risks.append({
                "key": f"risk-{index}",
                "title": title or f"风险点{risk_index}",
                "level": self._extract_bullet_value(block, "风险等级") or "中",
                "description": self._extract_bullet_value(block, "风险描述"),
                "impact": self._extract_bullet_value(block, "影响范围"),
                "strategy": self._extract_bullet_value(block, "应对策略"),
            })
        return risks

    def _parse_pending_unknown_items(self, content: str) -> list[dict]:
        section = self._extract_subsection(content, "### 10.1 未明确信息")
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return []
        items: list[dict] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 1 and cells[0] and cells[0] != "---":
                text = " / ".join(cell for cell in cells[1:] if cell)
                items.append({
                    "title": cells[0],
                    "text": text,
                    "checked": False,
                })
        return items

    def _parse_assumptions(self, content: str) -> list[dict]:
        section = self._extract_subsection(content, "### 10.2 关键假设")
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
        if len(lines) <= 2:
            return []
        items: list[dict] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            if len(cells) >= 1 and cells[0] and cells[0] != "---":
                items.append({
                    "title": cells[0],
                    "text": " / ".join(cell for cell in cells[1:] if cell),
                })
        return items

    def _extract_bullet_value(self, content: str, label: str) -> str:
        match = re.search(rf"-\s*{re.escape(label)}：\s*(.*)", content)
        return match.group(1).strip() if match else ""

    def _extract_numbered_block(self, content: str, label: str) -> str:
        match = re.search(rf"-\s*{re.escape(label)}：\s*\n((?:\s*\d+\.\s.*\n?)*)", content)
        return match.group(1).strip() if match else ""

    def _hydrate_project_config(self, project: Project) -> Project:
        base_config = dict(project.config or {})
        if self.requirement_repo is not None:
            analysis = self.requirement_repo.load(project.project_id)
            if analysis is not None:
                base_config["requirementAnalysis"] = analysis
            else:
                file_config = self.store.read_json(project_config_path(project), default={}) or {}
                fallback_analysis = dict(file_config.get("requirementAnalysis") or {})
                if fallback_analysis:
                    merged = self._merge_requirement_analysis(self._create_default_requirement_analysis(), fallback_analysis)
                    self.requirement_repo.save_full(project.project_id, merged)
                    base_config["requirementAnalysis"] = merged
        else:
            file_config = self.store.read_json(project_config_path(project), default={}) or {}
            base_config = {**file_config, **base_config}

        project.config = self._normalize_config(base_config)
        return project

    def delete_project(self, project_id: str, user_id: str) -> None:
        project = self.get_project_for_user(project_id, user_id)
        project_dir = Path(project.workspace_path)
        if self.header_store is not None:
            self.header_store.delete_project(project_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)
