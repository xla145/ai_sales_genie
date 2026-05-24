from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from langgraph_prototype_project.cli import main as cli_main
from langgraph_prototype_project.models import DataEntityContract, MenuItemContract, PageContract, PrototypeContract, ValidationResult
from langgraph_prototype_project.skills import load_skill, skill_file_path, skills_root
from langgraph_prototype_project.validators import validate_outputs, validate_prototype_semantics
from langgraph_prototype_project.workflow import run_workflow


class WorkflowTests(unittest.TestCase):
    def test_workflow_generates_final_prototype_artifacts(self):
        with tempfile.TemporaryDirectory() as temp_dir, _configured_test_llm():
            result = run_workflow("客户管理系统，页面：首页、客户列表、客户详情", Path(temp_dir), parallel_workers=3)

            self.assertEqual(result.status, "success", result.error_message)
            self.assertIsNotNone(result.prototype_dir)
            workspace = result.workspace_dir
            expected = [
                "prototype/index.html",
                "prototype/assets/css/styles.css",
                "prototype/assets/js/app.js",
                "prototype/assets/js/mock-data.js",
                "generation-report.md",
                "validation-report.md",
            ]
            for relative_path in expected:
                self.assertTrue((workspace / relative_path).exists(), relative_path)
            self.assertFalse((workspace / "需求结构化.md").exists())
            self.assertFalse((workspace / "页面详细设计").exists())
            self.assertGreaterEqual(len(list((workspace / "prototype" / "pages").glob("*.html"))), 3)
            self.assertTrue(all(item.ok for item in result.validations))
            report = (workspace / "generation-report.md").read_text(encoding="utf-8")
            self.assertIn("LLM 模型：test-model", report)
            self.assertIn("Skill 根目录：", report)
            self.assertIn("## 运行诊断", report)

    def test_cli_check_reports_preflight_status(self):
        with tempfile.TemporaryDirectory() as temp_dir, _configured_test_llm():
            with patch.object(sys, "argv", ["langgraph-prototype", "--check", "--output-dir", temp_dir]):
                self.assertEqual(cli_main(), 0)

    def test_skill_root_can_be_configured(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill_dir = root / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Demo", encoding="utf-8")
            try:
                with patch.dict(os.environ, {"LANGGRAPH_PROTOTYPE_SKILLS_ROOT": str(root)}):
                    skills_root.cache_clear()
                    load_skill.cache_clear()
                    self.assertEqual(skill_file_path("demo-skill").resolve(), (skill_dir / "SKILL.md").resolve())
                    self.assertEqual(load_skill("demo-skill"), "# Demo")
            finally:
                skills_root.cache_clear()
                load_skill.cache_clear()

    def test_validation_reports_missing_and_empty_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            (workspace / "present.md").write_text("ok", encoding="utf-8")
            (workspace / "empty.md").write_text("", encoding="utf-8")

            result = validate_outputs(workspace, "test", ("present.md", "empty.md", "missing.md"))

            self.assertIsInstance(result, ValidationResult)
            self.assertFalse(result.ok)
            self.assertEqual(result.missing, ("missing.md",))
            self.assertEqual(result.empty, ("empty.md",))

    def test_macro_stage_order_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp_dir, _configured_test_llm():
            result = run_workflow("库存管理原型", Path(temp_dir), parallel_workers=2)

            self.assertEqual([item.stage for item in result.validations], [
                "requirement_intake",
                "system_design",
                "prototype_generation",
            ])

    def test_semantic_validation_rejects_broken_local_link(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            _write_valid_prototype(workspace, pages=("首页",))
            (workspace / "prototype" / "pages" / "首页.html").write_text(_page_html("首页", "./missing.html"), encoding="utf-8")

            result = validate_prototype_semantics(workspace, ["首页"])

            self.assertFalse(result.ok)
            self.assertTrue(any("broken local link" in issue for issue in result.issues))

    def test_semantic_validation_rejects_failed_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            _write_valid_prototype(workspace, pages=("首页",))
            (workspace / "validation-report.md").write_text("# 校验报告\n\n总体结论：不通过", encoding="utf-8")

            result = validate_prototype_semantics(workspace, ["首页"])

            self.assertFalse(result.ok)
            self.assertTrue(any("validation-report" in issue for issue in result.issues))

    def test_semantic_validation_rejects_undefined_global_function(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            _write_valid_prototype(workspace, pages=("首页",))
            (workspace / "prototype" / "assets" / "js" / "app.js").write_text("window.App = {};", encoding="utf-8")
            (workspace / "prototype" / "pages" / "首页.html").write_text(_page_html("首页", "./首页.html") + "<script>showToast('x');</script>", encoding="utf-8")

            result = validate_prototype_semantics(workspace, ["首页"])

            self.assertFalse(result.ok)
            self.assertTrue(any("undefined global function" in issue or "app.js missing utility" in issue for issue in result.issues))

    def test_semantic_validation_requires_expected_pages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            _write_valid_prototype(workspace, pages=("首页",))

            result = validate_prototype_semantics(workspace, ["首页", "客户列表"])

            self.assertFalse(result.ok)
            self.assertTrue(any("expected page" in issue for issue in result.issues))

    def test_semantic_validation_rejects_inconsistent_navigation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            pages = ("首页", "客户列表", "客户详情")
            _write_valid_prototype(workspace, pages=pages)
            contract = _contract(pages)
            bad_nav = '<a class="nav-link active" href="./首页.html">首页</a><a class="nav-link" href="./客户详情.html">客户详情</a>'
            (workspace / "prototype" / "pages" / "客户列表.html").write_text(_page_html("客户列表", "./首页.html", bad_nav), encoding="utf-8")

            result = validate_prototype_semantics(workspace, list(pages), contract)

            self.assertFalse(result.ok)
            self.assertTrue(any("navigation mismatch" in issue for issue in result.issues))

    def test_semantic_validation_rejects_missing_active_navigation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            pages = ("首页", "客户列表")
            _write_valid_prototype(workspace, pages=pages)
            contract = _contract(pages)
            nav = ''.join(f'<a class="nav-link" href="./{page}.html">{page}</a>' for page in pages)
            (workspace / "prototype" / "pages" / "客户列表.html").write_text(_page_html("客户列表", "./首页.html", nav), encoding="utf-8")

            result = validate_prototype_semantics(workspace, list(pages), contract)

            self.assertFalse(result.ok)
            self.assertTrue(any("active state" in issue for issue in result.issues))

    def test_semantic_validation_rejects_mock_data_contract_gap(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            pages = ("首页", "客户列表")
            _write_valid_prototype(workspace, pages=pages)
            contract = _contract(pages)
            (workspace / "prototype" / "assets" / "js" / "mock-data.js").write_text("window.MockData={users:[],roles:[],navMenus:[]};", encoding="utf-8")

            result = validate_prototype_semantics(workspace, list(pages), contract)

            self.assertFalse(result.ok)
            self.assertTrue(any("mock-data.js missing entity" in issue for issue in result.issues))


class _configured_test_llm:
    def __enter__(self):
        self.env_patch = patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "OPENAI_MODEL": "test-model"})
        self.complete_patch = patch("langgraph_prototype_project.workflow.complete_json", new=_fake_complete_json)
        self.env_patch.__enter__()
        self.complete_patch.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.complete_patch.__exit__(exc_type, exc, tb)
        self.env_patch.__exit__(exc_type, exc, tb)


async def _fake_complete_json(config, system_prompt: str, user_prompt: str) -> dict:
    if "requirement-intake-structuring" in system_prompt:
        return {"files": [{"path": "需求结构化.md", "content": "# 需求结构化\n\n## 1. 输入理解摘要\n完整\n## 5. 功能需求\n完整"}]}
    if "system-function-design-planning" in system_prompt:
        files = []
        if "系统全局功能描述与设计.md" in user_prompt:
            files.append({"path": "系统全局功能描述与设计.md", "content": "# 系统全局功能描述与设计\n\n客户管理系统完整设计"})
        if "系统的功能点设计.md" in user_prompt:
            files.append({"path": "系统的功能点设计.md", "content": _feature_design()})
        for page in ("首页", "客户列表", "客户详情"):
            if f"页面详细设计/{page}.md" in user_prompt:
                files.append({"path": f"页面详细设计/{page}.md", "content": f"# {page}\n\n组件：页面标题、主导航、筛选、列表、详情、操作\n操作：查看、提交、返回\n跳转关系：首页、客户列表、客户详情\n原型生成说明：完整体现 {page}"})
        if "第二阶段设计检查报告.md" in user_prompt:
            files.append({"path": "第二阶段设计检查报告.md", "content": "# 第二阶段设计检查报告\n\n通过"})
        return {"files": files or [
            {"path": "系统全局功能描述与设计.md", "content": "# 系统全局功能描述与设计\n\n完整"},
            {"path": "系统的功能点设计.md", "content": _feature_design()},
            {"path": "页面详细设计/首页.md", "content": "# 首页\n\n组件：页面标题、主导航、指标、趋势、待办\n操作：查看、提交、返回"},
            {"path": "页面详细设计/客户列表.md", "content": "# 客户列表\n\n组件：页面标题、主导航、筛选、列表、操作\n操作：查看、提交、返回"},
            {"path": "页面详细设计/客户详情.md", "content": "# 客户详情\n\n组件：页面标题、主导航、详情、关联记录、返回\n操作：查看、提交、返回"},
            {"path": "第二阶段设计检查报告.md", "content": "# 第二阶段设计检查报告\n\n通过"},
        ]}
    return _fake_prototype_response(user_prompt)


def _feature_design() -> str:
    return """# 系统的功能点设计

| 页面名称 | 路由路径 | 菜单名称 | 父级菜单 | 承载功能点 | 跳转关系 |
|---|---|---|---|---|---|
| 首页 | prototype/pages/首页.html | 首页 |  | 指标、待办 | 客户列表 |
| 客户列表 | prototype/pages/客户列表.html | 客户列表 |  | 筛选、列表、查看 | 首页、客户详情 |
| 客户详情 | prototype/pages/客户详情.html | 客户详情 | 客户列表 | 详情、关联记录 | 客户列表 |
"""


def _fake_prototype_response(user_prompt: str) -> dict:
    if "一次性生成公共原型文件" in user_prompt:
        shared = [item for item in _valid_prototype_files(("首页", "客户列表", "客户详情")) if not item[0].startswith("prototype/pages/") and not item[0].endswith("report.md")]
        return {"files": [{"path": path, "content": content} for path, content in shared]}
    allowed_marker = "只允许生成文件："
    target_path = None
    if allowed_marker in user_prompt:
        target_path = user_prompt.rsplit(allowed_marker, 1)[1].strip().split()[0]
    for path, content in _valid_prototype_files(("首页", "客户列表", "客户详情")):
        if path == target_path:
            return {"files": [{"path": path, "content": content}]}
    return {"files": [{"path": "validation-report.md", "content": "# 校验报告\n\n验收结论：通过"}]}


def _write_valid_prototype(workspace: Path, pages: tuple[str, ...]) -> None:
    for path, content in _valid_prototype_files(pages):
        target = workspace / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _valid_prototype_files(pages: tuple[str, ...]):
    page_links = "".join(f'<a class="nav-link{ " active" if index == 0 else "" }" href="./{page}.html" aria-current="{ "page" if index == 0 else "false" }">{page}</a>' for index, page in enumerate(pages))
    root_links = "".join(f'<a href="./pages/{page}.html">{page}</a>' for page in pages)
    yield "prototype/index.html", f"<!doctype html><html><head><link rel='stylesheet' href='./assets/css/styles.css'></head><body>{root_links}<script src='./assets/js/mock-data.js'></script><script src='./assets/js/app.js'></script></body></html>"
    yield "prototype/README.md", "# 原型说明\n\n路由清单完整"
    yield "prototype/assets/css/styles.css", "body{font-family:sans-serif}.app-shell{}.sidebar{}.topbar{}.nav-link{display:block}.nav-link.active{font-weight:bold}.page-header{}.stat-card{}.data-table{}.filter-bar{}.form-grid{}.status-badge{}.modal{}.empty-state{}.toast{}"
    yield "prototype/assets/js/app.js", "function showToast(){} function openModal(){} function closeModal(){} function validateRequired(){return true} function submitWithLoading(){} function toggleSidebar(){} function getCurrentUser(){return MockData.currentUser} function setCurrentNav(){} window.showToast=showToast; window.openModal=openModal; window.closeModal=closeModal; window.validateRequired=validateRequired; window.submitWithLoading=submitWithLoading; window.toggleSidebar=toggleSidebar; window.getCurrentUser=getCurrentUser; window.setCurrentNav=setCurrentNav; window.App={showToast,openModal,closeModal,validateRequired,submitWithLoading,toggleSidebar,getCurrentUser,setCurrentNav};"
    yield "prototype/assets/js/mock-data.js", "const users=[{id:'U1',name:'demo',role:'admin',department:'销售部'}]; const roles=[{id:'R1',name:'admin',permissions:['*']}]; const navMenus=[{key:'home',label:'首页',href:'./首页.html',order:1}]; const customers=[{id:'C1',name:'客户A',status:'active',ownerId:'U1',updatedAt:'2026-01-01'}]; const notifications=[]; const todoItems=[]; window.MockData={users,roles,navMenus,customers,notifications,todoItems,currentUser:users[0]};"
    for page in pages:
        yield f"prototype/pages/{page}.html", _page_html(page, f"./{pages[0]}.html", _nav_for_pages(pages, page))
    yield "generation-report.md", "# 生成报告\n\nprototype/pages/首页.html\nprototype/pages/客户列表.html\nprototype/pages/客户详情.html"
    yield "validation-report.md", "# 校验报告\n\n验收结论：通过"


def _page_html(page: str, extra_link: str, nav: str | None = None) -> str:
    nav = nav or f'<a class="nav-link active" href="./{page}.html" aria-current="page">{page}</a><a class="nav-link" href="./{page}.html">返回</a>'
    return f"<!doctype html><html><head><link rel='stylesheet' href='../assets/css/styles.css'></head><body><div class='app-shell'><aside class='sidebar'><nav>{nav}</nav></aside><main><header class='page-header'><h1>{page}</h1></header><section class='filter-bar'>筛选 页面标题 主导航</section><section class='stat-card'>指标 趋势 待办</section><section class='data-table'>列表 详情 关联记录 字段 表单 操作 查看 提交 返回 {page}</section><a href='{extra_link}'>操作</a><button onclick=\"showToast('ok')\">提交</button></main></div><script src='../assets/js/mock-data.js'></script><script src='../assets/js/app.js'></script></body></html>"


def _nav_for_pages(pages: tuple[str, ...], active_page: str) -> str:
    return "".join(f'<a class="nav-link{ " active" if page == active_page else "" }" href="./{page}.html" aria-current="{ "page" if page == active_page else "false" }">{page}</a>' for page in pages)


def _contract(pages: tuple[str, ...]) -> PrototypeContract:
    page_contracts = tuple(PageContract(
        page_name=page,
        file_name=f"{page}.html",
        html_path=f"prototype/pages/{page}.html",
        feature_names=(page,),
        primary_actions=("查看", "提交", "返回"),
        allowed_links=tuple(f"./{item}.html" for item in pages),
        required_sections=(page, "页面标题", "主导航", "操作"),
        current_nav_key=page,
    ) for page in pages)
    menus = tuple(MenuItemContract(key=page, label=page, href=f"./{page}.html", order=index + 1, page_name=page) for index, page in enumerate(pages))
    entities = (DataEntityContract("客户", "customers", ("id", "name", "status", "ownerId", "updatedAt"), used_by_pages=pages),)
    return PrototypeContract("客户管理系统", page_contracts, menus, data_entities=entities)


if __name__ == "__main__":
    unittest.main()
