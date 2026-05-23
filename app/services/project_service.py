from __future__ import annotations

from datetime import datetime
from pathlib import Path
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
from app.storage.file_store import FileStore
from app.storage.header_paths import project_config_path, project_file_path
from app.storage.header_store import HeaderStore


class ProjectService:
    def __init__(self, base_dir: Path, header_store: HeaderStore | None = None) -> None:
        self.base_dir = base_dir
        self.projects_dir = self.base_dir / "data" / "projects"
        self.store = FileStore()
        self.header_store = header_store
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create_project(self, payload: CreateProjectRequest) -> Project:
        now = datetime.now()
        project_id = f"proj_{uuid4().hex[:8]}"
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=False)

        project = Project(
            project_id=project_id,
            name=payload.name,
            description=payload.description,
            status=ProjectStatus.CREATED,
            workspace_path=str(project_dir),
            config=payload.config,
            created_at=now,
            updated_at=now,
        )
        self.store.write_json(project_file_path(project), project.model_dump(mode="json"))
        self.store.write_json(project_config_path(project), payload.config)
        if self.header_store is not None:
            self.header_store.upsert_project(project)
        return project

    def get_project(self, project_id: str) -> Project:
        if self.header_store is not None:
            project = self.header_store.get_project(project_id)
            if project is None:
                raise FileNotFoundError(project_id)
            return self._hydrate_project_config(project)

        project_path = self.projects_dir / project_id / "project.json"
        data = self.store.read_json(project_path)
        if not data:
            raise FileNotFoundError(project_id)
        return Project.model_validate(data)

    def list_projects(self) -> list[Project]:
        if self.header_store is not None:
            return [self._hydrate_project_config(project) for project in self.header_store.list_projects()]

        projects: list[Project] = []
        for project_file in sorted(self.projects_dir.glob("*/project.json")):
            data = self.store.read_json(project_file)
            if data:
                projects.append(Project.model_validate(data))
        return projects

    def save_project(self, project: Project) -> None:
        project.updated_at = datetime.now()
        self.store.write_json(project_file_path(project), project.model_dump(mode="json"))
        self.store.write_json(project_config_path(project), project.config)
        if self.header_store is not None:
            self.header_store.upsert_project(project)

    def update_project(self, project_id: str, payload: UpdateProjectRequest) -> Project:
        project = self.get_project(project_id)
        project.name = payload.name
        project.description = payload.description
        project.config = payload.config
        self.save_project(project)
        return project

    def update_project_overview(self, project_id: str, payload: UpdateProjectOverviewRequest) -> Project:
        project = self.get_project(project_id)
        if payload.name is not None:
            project.name = payload.name
        if payload.description is not None:
            project.description = payload.description

        config = dict(project.config or {})
        for key in ('clientInfo', 'province', 'city', 'stage', 'industry'):
            value = getattr(payload, key)
            if value is not None:
                config[key] = value

        project.config = config
        self.save_project(project)
        return project

    def update_requirement_analysis(self, project_id: str, payload: UpdateRequirementAnalysisRequest) -> Project:
        project = self.get_project(project_id)
        config = dict(project.config or {})
        requirement_analysis = dict(config.get('requirementAnalysis') or {})

        if payload.basic:
            requirement_analysis['basic'] = {
                **dict(requirement_analysis.get('basic') or {}),
                **payload.basic,
            }
        if payload.core:
            requirement_analysis['core'] = {
                **dict(requirement_analysis.get('core') or {}),
                **payload.core,
            }
        if payload.scenarios is not None:
            requirement_analysis['scenarios'] = payload.scenarios
        if payload.functions:
            requirement_analysis['functions'] = {
                **dict(requirement_analysis.get('functions') or {}),
                **payload.functions,
            }
        if payload.risks is not None:
            requirement_analysis['risks'] = payload.risks
        if payload.pending:
            requirement_analysis['pending'] = {
                **dict(requirement_analysis.get('pending') or {}),
                **payload.pending,
            }
        if payload.attachments is not None:
            requirement_analysis['attachments'] = payload.attachments
        if payload.supplement:
            requirement_analysis['supplement'] = {
                **dict(requirement_analysis.get('supplement') or {}),
                **payload.supplement,
            }

        config['requirementAnalysis'] = requirement_analysis
        project.config = config
        self.save_project(project)
        return project

    def read_phase1_requirement_doc(self, project_id: str) -> str:
        project = self.get_project(project_id)
        target = Path(project.workspace_path) / '需求结构化.md'
        if not target.exists():
            raise FileNotFoundError(target.name)
        return target.read_text(encoding='utf-8')

    def build_requirement_analysis_from_phase1(self, project_id: str) -> dict:
        content = self.read_phase1_requirement_doc(project_id)
        project = self.get_project(project_id)
        existing = dict((project.config or {}).get('requirementAnalysis') or {})
        defaults = self._create_default_requirement_analysis()

        basic_info = self._parse_named_table(content, '## 2. 项目基础信息')
        background = self._parse_named_table(content, '### 3.1 项目背景')
        goals = self._parse_named_table(content, '### 3.2 项目目标')
        users = self._parse_core_users(content)
        pain_points = self._parse_pain_points(content)
        scenarios = self._parse_scenarios(content)
        explicit_functions = self._parse_markdown_table_rows(content, '### 5.1 显性功能点')
        latent_functions = self._parse_markdown_table_rows(content, '### 5.2 潜在功能点')
        tech_requirements = self._parse_named_table(content, '## 6. 技术需求')
        non_function_requirements = self._parse_named_table(content, '## 7. 非功能需求')
        constraints = self._parse_named_table(content, '## 8. 约束条件')
        risks = self._parse_risks(content)
        pending_unknown_items = self._parse_pending_unknown_items(content)
        assumptions = self._parse_assumptions(content)

        pending_unknown_summary = '\n'.join(item['text'] for item in pending_unknown_items)
        assumption_summary = '\n'.join(
            f"{item['title']}：{item['text']}" if item['title'] else item['text']
            for item in assumptions
        )

        existing_basic = dict(existing.get('basic') or {})
        existing_core = dict(existing.get('core') or {})
        existing_functions = dict(existing.get('functions') or {})
        existing_pending = dict(existing.get('pending') or {})
        existing_supplement = dict(existing.get('supplement') or {})

        return {
            **defaults,
            **existing,
            'basic': {
                **defaults['basic'],
                **existing_basic,
                'projectName': basic_info.get('项目名称', existing_basic.get('projectName', '')),
                'projectSummary': basic_info.get('项目摘要', existing_basic.get('projectSummary', '')),
                'industry': basic_info.get('对应行业', existing_basic.get('industry', '')),
                'projectType': basic_info.get('项目类型', existing_basic.get('projectType', '')),
                'keywords': basic_info.get('项目关键词', existing_basic.get('keywords', '')),
            },
            'core': {
                **defaults['core'],
                **existing_core,
                'background': '\n'.join(filter(None, [
                    background.get('项目背景', ''),
                    background.get('立项原因', ''),
                    background.get('当前现状', ''),
                ])).strip(),
                'goal': '\n'.join(filter(None, [
                    goals.get('业务目标（显性）', ''),
                    goals.get('用户目标（隐性）', ''),
                    goals.get('成功指标', ''),
                ])).strip(),
                'users': users or existing_core.get('users', ''),
                'painPoints': pain_points or existing_core.get('painPoints', ''),
            },
            'scenarios': scenarios or existing.get('scenarios') or defaults['scenarios'],
            'functions': {
                'functionDesc': {
                    **defaults['functions']['functionDesc'],
                    **dict(existing_functions.get('functionDesc') or {}),
                    '显性核心功能点': explicit_functions,
                    '潜在功能点': latent_functions,
                    '技术选型': tech_requirements.get('技术选型', ''),
                    '技术架构': tech_requirements.get('技术架构', ''),
                    '依赖系统': tech_requirements.get('依赖系统', ''),
                },
                'nonFunction': {
                    **defaults['functions']['nonFunction'],
                    **dict(existing_functions.get('nonFunction') or {}),
                    '性能要求': non_function_requirements.get('性能要求', ''),
                    '可用性要求': non_function_requirements.get('可用性要求', ''),
                    '安全性要求': non_function_requirements.get('安全性要求', ''),
                    '兼容性要求': non_function_requirements.get('兼容性要求', ''),
                },
                'constraints': {
                    **defaults['functions']['constraints'],
                    **dict(existing_functions.get('constraints') or {}),
                    '性能约束': constraints.get('性能约束', ''),
                    '可用性约束': constraints.get('可用性约束', ''),
                    '安全性约束': constraints.get('安全性约束', ''),
                    '兼容性约束': constraints.get('兼容性约束', ''),
                },
            },
            'risks': risks or existing.get('risks') or defaults['risks'],
            'pending': {
                **defaults['pending'],
                **existing_pending,
                'unknownInfo': pending_unknown_summary or existing_pending.get('unknownInfo', ''),
                'assumptions': assumption_summary or existing_pending.get('assumptions', ''),
                'items': pending_unknown_items or existing_pending.get('items') or defaults['pending']['items'],
            },
            'attachments': existing.get('attachments') or [],
            'supplement': {
                **defaults['supplement'],
                **existing_supplement,
                'notes': existing_supplement.get('notes', ''),
            },
        }

    def sync_requirement_analysis_from_phase1(self, project_id: str) -> Project:
        project = self.get_project(project_id)
        config = dict(project.config or {})
        config['requirementAnalysis'] = self.build_requirement_analysis_from_phase1(project_id)
        project.config = config
        self.save_project(project)
        return project

    def _create_default_requirement_analysis(self) -> dict:
        return {
            'basic': {
                'projectName': '',
                'projectSummary': '',
                'industry': '',
                'projectType': '',
                'keywords': '',
            },
            'core': {
                'background': '',
                'goal': '',
                'users': '',
                'painPoints': '',
            },
            'scenarios': [{'key': 'scenario-1', 'title': '场景1', 'description': '', 'flow': ''}],
            'functions': {
                'functionDesc': {
                    '显性核心功能点': '',
                    '潜在功能点': '',
                    '技术选型': '',
                    '技术架构': '',
                    '依赖系统': '',
                },
                'nonFunction': {
                    '性能要求': '',
                    '可用性要求': '',
                    '安全性要求': '',
                    '兼容性要求': '',
                },
                'constraints': {
                    '性能约束': '',
                    '可用性约束': '',
                    '安全性约束': '',
                    '兼容性约束': '',
                },
            },
            'risks': [{'key': 'risk-1', 'title': '风险点1', 'level': '中', 'description': '', 'impact': '', 'strategy': ''}],
            'pending': {
                'unknownInfo': '',
                'assumptions': '',
                'items': [
                    {'title': '待确认事项1', 'text': '', 'checked': False},
                ],
            },
            'attachments': [],
            'supplement': {
                'notes': '',
            },
        }

    def _extract_section(self, content: str, heading: str) -> str:
        start = content.find(heading)
        if start == -1:
            return ''
        next_heading = re.search(r'\n##\s+\d+\.|\n##\s+[^\n]+', content[start + len(heading):])
        if next_heading:
            end = start + len(heading) + next_heading.start()
            return content[start:end].strip()
        return content[start:].strip()

    def _extract_subsection(self, content: str, heading: str) -> str:
        start = content.find(heading)
        if start == -1:
            return ''
        next_heading = re.search(r'\n###\s+|\n##\s+', content[start + len(heading):])
        if next_heading:
            end = start + len(heading) + next_heading.start()
            return content[start:end].strip()
        return content[start:].strip()

    def _parse_markdown_table_rows(self, content: str, heading: str) -> str:
        section = self._extract_subsection(content, heading)
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return ''
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            meaningful = [cell for cell in cells if cell and cell != '---']
            if meaningful:
                rows.append(' / '.join(meaningful))
        return '\n'.join(rows)

    def _parse_named_table(self, content: str, heading: str) -> dict[str, str]:
        section = self._extract_subsection(content, heading)
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return {}
        result: dict[str, str] = {}
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 2 and cells[0] and cells[0] != '---':
                result[cells[0]] = cells[1]
        return result

    def _parse_core_users(self, content: str) -> str:
        section = self._extract_subsection(content, '### 3.3 核心用户')
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return ''
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 4 and any(cells[:4]):
                rows.append(' / '.join(cell for cell in cells[:4] if cell))
        return '\n'.join(rows)

    def _parse_pain_points(self, content: str) -> str:
        section = self._extract_subsection(content, '### 3.4 当前痛点')
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return ''
        rows: list[str] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 3 and any(cells[:3]):
                rows.append(' / '.join(cell for cell in cells[:3] if cell))
        return '\n'.join(rows)

    def _parse_scenarios(self, content: str) -> list[dict]:
        section = self._extract_section(content, '## 4. 场景与诉求分析')
        matches = re.findall(r'###\s+场景\s*(\d+)：(.*?)(?=\n###\s+场景\s*\d+：|\n##\s+5\.|\Z)', section, flags=re.S)
        scenarios: list[dict] = []
        for index, (_, block) in enumerate(matches, start=1):
            title_match = re.search(r'^(.*?)\n', block.strip())
            title = title_match.group(1).strip() if title_match else f'场景{index}'
            description = self._extract_bullet_value(block, '场景描述')
            flow = self._extract_numbered_block(block, '场景流程')
            scenarios.append({
                'key': f'scenario-{index}',
                'title': title or f'场景{index}',
                'description': description,
                'flow': flow,
            })
        return scenarios

    def _parse_risks(self, content: str) -> list[dict]:
        section = self._extract_section(content, '## 9. 风险点与关注点')
        matches = re.findall(r'###\s+风险点\s*(\d+)：(.*?)(?=\n###\s+风险点\s*\d+：|\n##\s+10\.|\Z)', section, flags=re.S)
        risks: list[dict] = []
        for index, (risk_index, block) in enumerate(matches, start=1):
            title = block.strip().splitlines()[0].strip() if block.strip().splitlines() else f'风险点{risk_index}'
            risks.append({
                'key': f'risk-{index}',
                'title': title or f'风险点{risk_index}',
                'level': self._extract_bullet_value(block, '风险等级') or '中',
                'description': self._extract_bullet_value(block, '风险描述'),
                'impact': self._extract_bullet_value(block, '影响范围'),
                'strategy': self._extract_bullet_value(block, '应对策略'),
            })
        return risks

    def _parse_pending_unknown_items(self, content: str) -> list[dict]:
        section = self._extract_subsection(content, '### 10.1 未明确信息')
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return []
        items: list[dict] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 1 and cells[0] and cells[0] != '---':
                text = ' / '.join(cell for cell in cells[1:] if cell)
                items.append({
                    'title': cells[0],
                    'text': text,
                    'checked': False,
                })
        return items

    def _parse_assumptions(self, content: str) -> list[dict]:
        section = self._extract_subsection(content, '### 10.2 关键假设')
        lines = [line.strip() for line in section.splitlines() if line.strip().startswith('|')]
        if len(lines) <= 2:
            return []
        items: list[dict] = []
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) >= 1 and cells[0] and cells[0] != '---':
                items.append({
                    'title': cells[0],
                    'text': ' / '.join(cell for cell in cells[1:] if cell),
                })
        return items

    def _extract_bullet_value(self, content: str, label: str) -> str:
        match = re.search(rf'-\s*{re.escape(label)}：\s*(.*)', content)
        return match.group(1).strip() if match else ''

    def _extract_numbered_block(self, content: str, label: str) -> str:
        match = re.search(rf'-\s*{re.escape(label)}：\s*\n((?:\s*\d+\.\s.*\n?)*)', content)
        return match.group(1).strip() if match else ''

    def _hydrate_project_config(self, project: Project) -> Project:
        config_path = project_config_path(project)
        config = self.store.read_json(config_path, default={}) or {}
        project.config = dict(config)
        return project

    def delete_project(self, project_id: str) -> None:
        project = self.get_project(project_id)
        project_dir = Path(project.workspace_path)
        if self.header_store is not None:
            self.header_store.delete_project(project_id)
        if project_dir.exists():
            shutil.rmtree(project_dir)
