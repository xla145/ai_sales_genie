from __future__ import annotations

import asyncio
from pathlib import Path
from time import perf_counter
from uuid import uuid4
import re
import shutil

from langgraph.graph import END, START, StateGraph

from langgraph_prototype_project.llm import LLMConfig, complete_json, diagnose_llm_config
from langgraph_prototype_project.models import (
    DataEntityContract,
    MenuItemContract,
    PageContract,
    PrototypeContract,
    ValidationResult,
    WorkflowResult,
    WorkflowState,
)
from langgraph_prototype_project.skills import load_skill, skills_root
from langgraph_prototype_project.utils import (
    dedupe_pages,
    extract_pages,
    extract_route_rows,
    html_path_for_page,
    normalize_page_name,
    page_href_for_page,
    page_name_to_filename,
)
from langgraph_prototype_project.validators import (
    PROTOTYPE_OUTPUTS,
    REQUIREMENT_OUTPUTS,
    SYSTEM_DESIGN_OUTPUTS,
    validate_outputs,
    validate_prototype_semantics,
)


_SHARED_PROTOTYPE_OUTPUTS = (
    "prototype/index.html",
    "prototype/README.md",
    "prototype/assets/css/styles.css",
    "prototype/assets/js/app.js",
    "prototype/assets/js/mock-data.js",
)


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("requirement_intake", requirement_intake_node)
    graph.add_node("validate_requirement", validate_requirement_node)
    graph.add_node("system_design", system_design_node)
    graph.add_node("validate_system_design", validate_system_design_node)
    graph.add_node("prototype_generation", prototype_generation_node)
    graph.add_node("validate_prototype", validate_prototype_node)
    graph.add_node("complete", complete_node)
    graph.add_node("fail", fail_node)

    graph.add_edge(START, "requirement_intake")
    graph.add_edge("requirement_intake", "validate_requirement")
    graph.add_conditional_edges("validate_requirement", route_after_validation, {"ok": "system_design", "failed": "fail"})
    graph.add_edge("system_design", "validate_system_design")
    graph.add_conditional_edges("validate_system_design", route_after_validation, {"ok": "prototype_generation", "failed": "fail"})
    graph.add_edge("prototype_generation", "validate_prototype")
    graph.add_conditional_edges("validate_prototype", route_after_validation, {"ok": "complete", "failed": "fail"})
    graph.add_edge("complete", END)
    graph.add_edge("fail", END)
    return graph.compile()


def run_workflow(requirement: str, output_dir: Path, parallel_workers: int = 4) -> WorkflowResult:
    return asyncio.run(run_workflow_async(requirement, output_dir, parallel_workers=parallel_workers))


def repair_existing_workflow(requirement: str, workspace_dir: Path, parallel_workers: int = 4) -> WorkflowResult:
    return asyncio.run(repair_existing_workflow_async(requirement, workspace_dir, parallel_workers=parallel_workers))


async def repair_existing_workflow_async(requirement: str, workspace_dir: Path, parallel_workers: int = 4) -> WorkflowResult:
    config = LLMConfig.from_env()
    pages = _discover_pages(workspace_dir) or [item.stem for item in sorted((workspace_dir / "prototype" / "pages").glob("*.html"))] or extract_pages(requirement)
    contract = _build_prototype_contract(workspace_dir, pages, requirement)
    metrics = {"llm_calls": 0, "repair_attempts": 0}
    await _repair_prototype_until_valid(workspace_dir, requirement, contract, config, metrics)
    validation = validate_prototype_semantics(workspace_dir, list(contract.page_names), contract)
    _write_validation_report(workspace_dir, validation)
    if not validation.ok:
        return WorkflowResult(
            status="failed",
            workspace_dir=workspace_dir,
            prototype_dir=workspace_dir / "prototype" if (workspace_dir / "prototype").exists() else None,
            artifacts=tuple(_collect_existing_outputs(workspace_dir, PROTOTYPE_OUTPUTS)),
            validations=(validation,),
            error_message="prototype repair failed: " + "; ".join(validation.issues[:5]),
        )
    return WorkflowResult(
        status="success",
        workspace_dir=workspace_dir,
        prototype_dir=workspace_dir / "prototype",
        artifacts=tuple(_keep_final_deliverables(workspace_dir)),
        validations=(validation,),
    )


async def run_workflow_async(
    requirement: str,
    output_dir: Path,
    parallel_workers: int = 4,
) -> WorkflowResult:
    output_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = output_dir / f"run_{uuid4().hex[:8]}"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    llm_config = LLMConfig.from_env()

    state = await build_graph().ainvoke(
        {
            "requirement": requirement,
            "workspace_dir": str(workspace_dir),
            "status": "running",
            "artifacts": [],
            "validations": [],
            "pages": [],
            "prototype_dir": None,
            "parallel_workers": parallel_workers,
            "use_llm": True,
            "llm_model": llm_config.model,
            "llm_config": llm_config,
            "generation_metrics": {"llm_calls": 0, "repair_attempts": 0},
        }
    )
    return WorkflowResult(
        status=state.get("status", "failed"),
        workspace_dir=workspace_dir,
        prototype_dir=Path(state["prototype_dir"]) if state.get("prototype_dir") else None,
        artifacts=tuple(dict.fromkeys(state.get("artifacts", []))),
        validations=tuple(state.get("validations", [])),
        error_message=state.get("error_message"),
    )


async def requirement_intake_node(state: WorkflowState) -> dict:
    workspace_dir = Path(state["workspace_dir"])
    artifacts = await _write_llm_requirement_structure(workspace_dir, state["requirement"], state["llm_config"], state.get("generation_metrics") or {})
    return {"current_stage": "requirement_intake", "artifacts": artifacts}


def validate_requirement_node(state: WorkflowState) -> dict:
    result = validate_outputs(Path(state["workspace_dir"]), "requirement_intake", REQUIREMENT_OUTPUTS)
    return _validation_update(result)


async def system_design_node(state: WorkflowState) -> dict:
    workspace_dir = Path(state["workspace_dir"])
    artifacts, pages = await _write_llm_system_design(
        workspace_dir,
        state["requirement"],
        int(state.get("parallel_workers") or 1),
        state["llm_config"],
        state.get("generation_metrics") or {},
    )
    return {"current_stage": "system_design", "artifacts": artifacts, "pages": pages}


def validate_system_design_node(state: WorkflowState) -> dict:
    result = validate_outputs(Path(state["workspace_dir"]), "system_design", SYSTEM_DESIGN_OUTPUTS)
    return _validation_update(result)


async def prototype_generation_node(state: WorkflowState) -> dict:
    pages = state.get("pages") or ["首页"]
    artifacts, contract, metrics = await _write_llm_prototype(
        Path(state["workspace_dir"]),
        pages,
        state["requirement"],
        int(state.get("parallel_workers") or 1),
        state["llm_config"],
        state.get("generation_metrics") or {},
    )
    return {
        "current_stage": "prototype_generation",
        "artifacts": artifacts,
        "prototype_dir": str(Path(state["workspace_dir"]) / "prototype"),
        "prototype_contract": contract,
        "pages": list(contract.page_names),
        "generation_metrics": metrics,
    }


def validate_prototype_node(state: WorkflowState) -> dict:
    result = validate_prototype_semantics(
        Path(state["workspace_dir"]),
        state.get("pages") or [],
        state.get("prototype_contract"),
    )
    _write_validation_report(Path(state["workspace_dir"]), result)
    return _validation_update(result)


def complete_node(state: WorkflowState) -> dict:
    workspace_dir = Path(state["workspace_dir"])
    final_artifacts = _keep_final_deliverables(workspace_dir)
    return {"status": "success", "artifacts": final_artifacts}


def _keep_final_deliverables(workspace_dir: Path) -> list[str]:
    keep = {"prototype", "generation-report.md", "validation-report.md"}
    for item in workspace_dir.iterdir():
        if item.name in keep:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    artifacts: list[str] = []
    prototype_dir = workspace_dir / "prototype"
    if prototype_dir.exists():
        artifacts.extend(str(path.relative_to(workspace_dir)) for path in sorted(prototype_dir.rglob("*")) if path.is_file())
    for report in ("generation-report.md", "validation-report.md"):
        if (workspace_dir / report).exists():
            artifacts.append(report)
    return artifacts


async def _write_llm_requirement_structure(workspace_dir: Path, requirement: str, config: LLMConfig, metrics: dict) -> list[str]:
    payload = await _generate_files(
        skill_name="requirement-intake-structuring",
        user_prompt=(
            "请严格按 skill 要求生成第一阶段文件。只返回 JSON。\n\n"
            f"原始需求：\n{requirement}\n\n"
            "必须生成文件：需求结构化.md"
        ),
        config=config,
        metrics=metrics,
    )
    written = _materialize_files(workspace_dir, payload, allowed_paths=("需求结构化.md",))
    await _repair_stage_outputs(workspace_dir, "requirement-intake-structuring", "requirement_intake", REQUIREMENT_OUTPUTS, requirement, config, metrics)
    return sorted(set(written + _collect_existing_outputs(workspace_dir, REQUIREMENT_OUTPUTS)))


async def _write_llm_system_design(workspace_dir: Path, requirement: str, parallel_workers: int, config: LLMConfig, metrics: dict) -> tuple[list[str], list[str]]:
    structured_requirement = (workspace_dir / "需求结构化.md").read_text(encoding="utf-8")
    fallback_pages = extract_pages(requirement)
    written: list[str] = []

    written.extend(await _generate_single_output(
        workspace_dir,
        "system-function-design-planning",
        "系统全局功能描述与设计.md",
        (
            "请严格按 skill 要求只生成第二阶段的系统全局功能描述与设计.md。只返回 JSON。\n\n"
            f"用户原始需求：\n{requirement}\n\n"
            f"需求结构化.md：\n{structured_requirement}\n\n"
            "只允许生成文件：系统全局功能描述与设计.md"
        ),
        config,
        metrics,
    ))
    system_design = (workspace_dir / "系统全局功能描述与设计.md").read_text(encoding="utf-8")
    written.extend(await _generate_single_output(
        workspace_dir,
        "system-function-design-planning",
        "系统的功能点设计.md",
        (
            "请严格按 skill 要求只生成第二阶段的系统的功能点设计.md。只返回 JSON。\n\n"
            "必须包含稳定的 Markdown 表格《菜单与路由规划》，表头至少包含：页面名称、路由路径、菜单名称、父级菜单、承载功能点、跳转关系。\n"
            "所有后续页面详细设计必须以该表格中的页面名称为准。\n\n"
            f"用户原始需求：\n{requirement}\n\n"
            f"需求结构化.md：\n{structured_requirement}\n\n"
            f"系统全局功能描述与设计.md：\n{system_design}\n\n"
            "只允许生成文件：系统的功能点设计.md"
        ),
        config,
        metrics,
    ))
    feature_design = (workspace_dir / "系统的功能点设计.md").read_text(encoding="utf-8")
    pages = _pages_from_feature_design(feature_design) or fallback_pages
    route_plan = _format_route_plan(feature_design, pages)

    page_tasks = [
        lambda page=page: _generate_single_output(
            workspace_dir,
            "system-function-design-planning",
            f"页面详细设计/{page}.md",
            (
                f"请严格按 skill 要求只生成页面详细设计/{page}.md。只返回 JSON。\n\n"
                f"用户原始需求：\n{requirement}\n\n"
                f"需求结构化.md：\n{structured_requirement}\n\n"
                f"系统全局功能描述与设计.md：\n{system_design}\n\n"
                f"系统的功能点设计.md：\n{feature_design}\n\n"
                f"统一菜单与路由规划：\n{route_plan}\n\n"
                f"目标页面：{page}\n"
                "页面详细设计必须明确页面目标、承载功能、核心组件、数据字段、业务状态、主要操作、异常/空状态、跳转关系和原型生成说明。\n"
                f"只允许生成文件：页面详细设计/{page}.md"
            ),
            config,
            metrics,
        )
        for page in pages
    ]
    for page_written in await _run_limited(page_tasks, parallel_workers):
        written.extend(page_written)

    page_context = _read_page_design_context(workspace_dir)
    written.extend(await _generate_single_output(
        workspace_dir,
        "system-function-design-planning",
        "第二阶段设计检查报告.md",
        (
            "请严格按 skill 要求只生成第二阶段设计检查报告.md。只返回 JSON。\n\n"
            f"用户原始需求：\n{requirement}\n\n"
            f"需求结构化.md：\n{structured_requirement}\n\n"
            f"系统全局功能描述与设计.md：\n{system_design}\n\n"
            f"系统的功能点设计.md：\n{feature_design}\n\n"
            f"页面详细设计：\n{page_context}\n\n"
            "检查重点：菜单与路由规划是否完整、每个功能点是否有页面承载、每个页面是否有跳转关系和原型生成说明。\n"
            "只允许生成文件：第二阶段设计检查报告.md"
        ),
        config,
        metrics,
    ))
    await _repair_stage_outputs(workspace_dir, "system-function-design-planning", "system_design", SYSTEM_DESIGN_OUTPUTS, requirement, config, metrics)
    pages = _discover_pages(workspace_dir) or pages
    return sorted(set(written + _collect_existing_outputs(workspace_dir, SYSTEM_DESIGN_OUTPUTS))), pages


async def _write_llm_prototype(workspace_dir: Path, pages: list[str], requirement: str, parallel_workers: int, config: LLMConfig, metrics: dict) -> tuple[list[str], PrototypeContract, dict]:
    start = perf_counter()
    page_files = sorted((workspace_dir / "页面详细设计").glob("*.md"))
    page_targets = [item.stem for item in page_files] or pages
    contract = _build_prototype_contract(workspace_dir, page_targets, requirement)
    _validate_prototype_contract(contract)
    written: list[str] = []
    compact_contract = _compact_contract_for_llm(contract)

    written.extend(await _generate_shared_prototype_assets(workspace_dir, compact_contract, requirement, config, metrics))

    page_tasks = []
    for page_file in page_files:
        page_name = page_file.stem
        page_design = page_file.read_text(encoding="utf-8")
        page_tasks.append(lambda page_name=page_name, page_design=page_design: _generate_single_output(
            workspace_dir,
            "prototype-generator",
            f"prototype/pages/{page_name_to_filename(page_name)}",
            (
                f"请严格按 prototype-generator skill 要求只生成 prototype/pages/{page_name_to_filename(page_name)}。只返回 JSON。\n\n"
                f"原型生成契约（必须严格遵守）：\n{compact_contract}\n\n"
                f"当前页面契约：\n{_format_page_contract(contract, page_name)}\n\n"
                f"当前页面详细设计：\n{page_design}\n\n"
                "业务页资源路径必须使用 ../assets/css/styles.css、../assets/js/mock-data.js、../assets/js/app.js。"
                "主导航必须静态写入 HTML，菜单项名称、顺序、href 必须与契约一致，当前页或父菜单必须高亮。"
                "所有 .html 跳转只能来自当前页面契约允许链接，禁止死链、契约外页面和“功能开发中”占位。"
                f"只允许生成文件：prototype/pages/{page_name_to_filename(page_name)}"
            ),
            config,
            metrics,
        ))
    for page_written in await _run_limited(page_tasks, parallel_workers):
        written.extend(page_written)

    metrics["duration_seconds"] = round(perf_counter() - start, 3)
    _write_generation_report(workspace_dir, contract, metrics)
    _write_validation_report(workspace_dir, ValidationResult(stage="prototype_generation", ok=True))
    await _repair_prototype_until_valid(workspace_dir, requirement, contract, config, metrics)
    validation = validate_prototype_semantics(workspace_dir, list(contract.page_names), contract)
    _write_validation_report(workspace_dir, validation)
    return sorted(set(written + _collect_existing_outputs(workspace_dir, PROTOTYPE_OUTPUTS))), contract, metrics


async def _generate_shared_prototype_assets(workspace_dir: Path, compact_contract: str, requirement: str, config: LLMConfig, metrics: dict) -> list[str]:
    return await _generate_allowed_outputs(
        workspace_dir,
        "prototype-generator",
        _SHARED_PROTOTYPE_OUTPUTS,
        (
            "请严格按 prototype-generator skill 要求一次性生成公共原型文件。只返回 JSON。\n\n"
            f"用户原始需求摘要：\n{requirement[:2000]}\n\n"
            f"原型生成契约（必须严格遵守）：\n{compact_contract}\n\n"
            "必须生成且只允许生成以下文件：\n"
            f"{chr(10).join(_SHARED_PROTOTYPE_OUTPUTS)}\n"
            "index.html 位于 prototype 根目录，资源路径使用 ./assets/...；README 必须列出实际页面；"
            "styles.css 必须提供契约中的公共组件类；app.js 必须暴露契约中的 JS API；mock-data.js 必须提供 users、roles、navMenus 和契约数据实体。"
        ),
        config,
        metrics,
    )


def _format_page_plan(page_targets: list[str]) -> str:
    return "\n".join(f"- {page} => {html_path_for_page(page)}" for page in page_targets)


def _pages_from_feature_design(feature_design: str) -> list[str]:
    pages: list[str] = []
    for row in extract_route_rows(feature_design):
        page_name = _find_row_value(row, "页面名称", "页面", "菜单名称", "菜单")
        if page_name:
            pages.append(page_name)
    return dedupe_pages(pages)


def _format_route_plan(feature_design: str, pages: list[str]) -> str:
    rows = extract_route_rows(feature_design)
    if rows:
        lines = []
        for row in rows:
            page = _find_row_value(row, "页面名称", "页面", "菜单名称", "菜单")
            route = _find_row_value(row, "路由路径", "路由", "路径", "文件") or html_path_for_page(page)
            menu = _find_row_value(row, "菜单名称", "菜单") or page
            parent = _find_row_value(row, "父级菜单", "父菜单")
            feature = _find_row_value(row, "承载功能点", "功能点", "功能")
            links = _find_row_value(row, "跳转关系", "跳转")
            lines.append(f"- 页面：{page}；路由：{route}；菜单：{menu}；父级：{parent or '-'}；功能：{feature or '-'}；跳转：{links or '-'}")
        return "\n".join(lines)
    return _format_page_plan(pages)


def _build_prototype_contract(workspace_dir: Path, pages: list[str], requirement: str) -> PrototypeContract:
    feature_design_path = workspace_dir / "系统的功能点设计.md"
    feature_design = feature_design_path.read_text(encoding="utf-8") if feature_design_path.is_file() else ""
    route_rows = extract_route_rows(feature_design)
    page_names = _pages_from_feature_design(feature_design) or dedupe_pages(pages)
    if not page_names:
        page_names = extract_pages(requirement)
    page_designs = _page_design_texts(workspace_dir)

    page_contracts: list[PageContract] = []
    menu_items: list[MenuItemContract] = []
    for index, page_name in enumerate(page_names):
        row = _route_row_for_page(route_rows, page_name)
        menu_label = _find_row_value(row, "菜单名称", "菜单") if row else ""
        parent_menu = _find_row_value(row, "父级菜单", "父菜单") if row else ""
        features = _split_contract_values(_find_row_value(row, "承载功能点", "功能点", "功能") if row else "")
        links = _links_for_page(page_name, page_names, row)
        sections = _required_sections(page_name, page_designs.get(page_name, ""), features)
        actions = _primary_actions(page_designs.get(page_name, ""), features)
        nav_key = _contract_key(parent_menu or menu_label or page_name)
        page_contracts.append(PageContract(
            page_name=page_name,
            file_name=page_name_to_filename(page_name),
            html_path=html_path_for_page(page_name),
            page_type=_infer_page_type(page_name, page_designs.get(page_name, "")),
            module_name=parent_menu or "核心业务",
            parent_menu=parent_menu or None,
            feature_names=tuple(features or [page_name]),
            primary_actions=tuple(actions),
            allowed_links=tuple(links),
            required_sections=tuple(sections),
            current_nav_key=nav_key,
        ))
        menu_items.append(MenuItemContract(
            key=nav_key,
            label=menu_label or parent_menu or page_name,
            href=page_href_for_page(page_name),
            order=index + 1,
            page_name=page_name,
            parent_key=_contract_key(parent_menu) if parent_menu else None,
        ))

    menu_items = _dedupe_menu_items(menu_items)
    entities = _infer_data_entities(page_contracts, requirement + "\n" + feature_design)
    return PrototypeContract(
        system_name=_infer_system_name(requirement),
        pages=tuple(page_contracts),
        menus=tuple(menu_items),
        data_entities=tuple(entities),
        metadata={"source": "system_design" if route_rows else "fallback"},
    )


def _validate_prototype_contract(contract: PrototypeContract) -> None:
    if not contract.pages:
        raise RuntimeError("Prototype contract must contain at least one page")
    page_names = [page.page_name for page in contract.pages]
    if len(page_names) != len(set(page_names)):
        raise RuntimeError("Prototype contract contains duplicate page names")
    paths = [page.html_path for page in contract.pages]
    if len(paths) != len(set(paths)):
        raise RuntimeError("Prototype contract contains duplicate page paths")
    page_hrefs = {page_href_for_page(page.page_name) for page in contract.pages}
    for menu in contract.menus:
        if menu.href not in page_hrefs:
            raise RuntimeError(f"Prototype menu points to unknown page: {menu.label} -> {menu.href}")


def _compact_contract_for_llm(contract: PrototypeContract) -> str:
    return "\n".join((
        f"系统名称：{contract.system_name}",
        "页面文件映射：",
        _format_page_plan(list(contract.page_names)),
        "统一主导航（所有业务页必须完全一致）：",
        _format_menu_contract(contract),
        "数据实体契约：",
        _format_data_contract(contract),
        "公共 JS API：" + "、".join(contract.js_api),
        "公共组件类：" + "、".join(contract.shared_components),
    ))


def _format_menu_contract(contract: PrototypeContract) -> str:
    return "\n".join(f"{item.order}. key={item.key} label={item.label} href={item.href} page={item.page_name}" for item in sorted(contract.menus, key=lambda item: item.order))


def _format_page_contract(contract: PrototypeContract, page_name: str) -> str:
    page = next((item for item in contract.pages if item.page_name == page_name), None)
    if page is None:
        return f"页面：{page_name}"
    return "\n".join((
        f"页面：{page.page_name}",
        f"文件：{page.html_path}",
        f"类型：{page.page_type}",
        f"当前导航 key：{page.current_nav_key or page.page_name}",
        "承载功能：" + "、".join(page.feature_names),
        "主要操作：" + "、".join(page.primary_actions),
        "允许链接：" + "、".join(page.allowed_links),
        "必备区块：" + "、".join(page.required_sections),
    ))


def _format_data_contract(contract: PrototypeContract) -> str:
    if not contract.data_entities:
        return "- users: id, name, role\n- roles: id, name\n- navMenus: key, label, href"
    return "\n".join(f"- {entity.js_key}: {', '.join(entity.fields or ('id', 'name', 'status'))}；关联页面：{', '.join(entity.used_by_pages)}" for entity in contract.data_entities)


async def _generate_single_output(workspace_dir: Path, skill_name: str, output_path: str, user_prompt: str, config: LLMConfig, metrics: dict) -> list[str]:
    return await _generate_allowed_outputs(workspace_dir, skill_name, (output_path,), user_prompt, config, metrics)


async def _generate_allowed_outputs(
    workspace_dir: Path,
    skill_name: str,
    allowed_paths: tuple[str, ...],
    user_prompt: str,
    config: LLMConfig,
    metrics: dict,
) -> list[str]:
    payload = await _generate_files(skill_name=skill_name, user_prompt=user_prompt, config=config, metrics=metrics)
    return _materialize_files(workspace_dir, payload, allowed_paths=allowed_paths)


async def _run_limited(task_factories, limit: int):
    semaphore = asyncio.Semaphore(max(1, limit))

    async def run(task_factory):
        async with semaphore:
            return await task_factory()

    return await asyncio.gather(*(run(task_factory) for task_factory in task_factories))


def _read_page_design_context(workspace_dir: Path) -> str:
    page_files = sorted((workspace_dir / "页面详细设计").glob("*.md"))
    return "\n\n".join(f"## {item.name}\n{item.read_text(encoding='utf-8')}" for item in page_files)


async def _generate_files(skill_name: str, user_prompt: str, config: LLMConfig, metrics: dict | None = None) -> dict:
    skill = load_skill(skill_name)
    system_prompt = (
        f"{skill}\n\n"
        "你必须严格遵守以上 skill。你在这个环境中不能直接调用文件工具，所以必须只返回 JSON："
        "{\"files\":[{\"path\":\"相对路径\",\"content\":\"完整文件内容\"}]}。"
        "不要返回 Markdown 代码围栏，不要返回解释。path 必须是相对路径，禁止绝对路径和 ..。"
    )
    if metrics is not None:
        metrics["llm_calls"] = int(metrics.get("llm_calls", 0)) + 1
    return await complete_json(config, system_prompt, user_prompt)


def _materialize_files(workspace_dir: Path, payload: dict, allowed_paths: tuple[str, ...] | None = None) -> list[str]:
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise RuntimeError("LLM JSON must contain non-empty files array")
    written: list[str] = []
    for item in files:
        if not isinstance(item, dict):
            continue
        relative_path = item.get("path")
        content = item.get("content")
        if not isinstance(relative_path, str) or not isinstance(content, str):
            continue
        if allowed_paths is not None and relative_path not in allowed_paths:
            continue
        target = _safe_workspace_path(workspace_dir, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_strip_code_fence(content), encoding="utf-8")
        written.append(str(target.relative_to(workspace_dir.resolve())))
    if not written:
        raise RuntimeError("LLM did not generate any allowed files")
    return written


def _safe_workspace_path(workspace_dir: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"Unsafe output path: {relative_path}")
    resolved = (workspace_dir / candidate).resolve()
    root = workspace_dir.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"Output path escapes workspace: {relative_path}")
    return resolved


def _discover_pages(workspace_dir: Path) -> list[str]:
    page_dir = workspace_dir / "页面详细设计"
    if not page_dir.exists():
        return []
    return [item.stem for item in sorted(page_dir.glob("*.md")) if item.is_file() and item.stat().st_size > 0]


def _collect_existing_outputs(workspace_dir: Path, expected_outputs: tuple[str, ...]) -> list[str]:
    outputs: list[str] = []
    for relative_path in expected_outputs:
        if "*" in relative_path:
            outputs.extend(str(item.relative_to(workspace_dir)) for item in sorted(workspace_dir.glob(relative_path)) if item.is_file())
            continue
        path = workspace_dir / relative_path
        if path.is_file():
            outputs.append(relative_path)
        elif path.is_dir():
            outputs.extend(str(item.relative_to(workspace_dir)) for item in sorted(path.rglob("*")) if item.is_file())
    return outputs


async def _repair_prototype_until_valid(workspace_dir: Path, requirement: str, contract: PrototypeContract, config: LLMConfig, metrics: dict, max_attempts: int = 3) -> None:
    for attempt in range(max_attempts):
        result = validate_prototype_semantics(workspace_dir, list(contract.page_names), contract)
        if result.ok:
            _write_validation_report(workspace_dir, result)
            return
        metrics["repair_attempts"] = int(metrics.get("repair_attempts", 0)) + 1
        allowed_paths = _allowed_prototype_repair_paths(workspace_dir, list(contract.page_names))
        payload = await _generate_files(
            skill_name="prototype-generator",
            user_prompt=(
                "前一次第三阶段原型未通过机器语义校验，请只修复下面列出的阻塞问题。只返回 JSON。\n\n"
                f"修复轮次：{attempt + 1}/{max_attempts}\n"
                f"原始需求：\n{requirement[:2000]}\n\n"
                f"原型生成契约（必须严格遵守）：\n{_compact_contract_for_llm(contract)}\n\n"
                f"当前文件清单：\n{chr(10).join(_collect_existing_outputs(workspace_dir, PROTOTYPE_OUTPUTS))}\n\n"
                f"缺失文件：{', '.join(result.missing)}\n"
                f"空文件：{', '.join(result.empty)}\n"
                f"阻塞问题：\n{chr(10).join(f'- {issue}' for issue in result.issues)}\n\n"
                "必须满足：所有业务页静态主导航一致且当前页高亮；所有本地 HTML 链接存在且来自契约；app.js 暴露页面调用的全局函数；"
                "mock-data.js 字段与页面和契约一致；核心操作不能只显示“功能开发中”；禁止生成契约外页面。\n"
                f"只允许生成或覆盖以下路径：\n{chr(10).join(allowed_paths)}"
            ),
            config=config,
            metrics=metrics,
        )
        _materialize_files(workspace_dir, payload, allowed_paths=tuple(allowed_paths))
        _write_validation_report(workspace_dir, ValidationResult(stage="prototype_generation", ok=True))


def _allowed_prototype_repair_paths(workspace_dir: Path, pages: list[str]) -> list[str]:
    paths = [
        "prototype/index.html",
        "prototype/README.md",
        "prototype/assets/css/styles.css",
        "prototype/assets/js/app.js",
        "prototype/assets/js/mock-data.js",
        "generation-report.md",
        "validation-report.md",
    ]
    paths.extend(html_path_for_page(page) for page in pages)
    paths.extend(str(path.relative_to(workspace_dir)) for path in sorted((workspace_dir / "prototype" / "pages").glob("*.html")))
    return sorted(dict.fromkeys(paths))


async def _repair_stage_outputs(
    workspace_dir: Path,
    skill_name: str,
    stage: str,
    expected_outputs: tuple[str, ...],
    context: str,
    config: LLMConfig,
    metrics: dict,
) -> None:
    result = validate_outputs(workspace_dir, stage, expected_outputs)
    if result.ok:
        return
    allowed_paths = _allowed_stage_repair_paths(workspace_dir, expected_outputs)
    payload = await _generate_files(
        skill_name=skill_name,
        user_prompt=(
            "前一次输出不完整，请根据同一个 skill 只补齐缺失或空文件。只返回 JSON。\n"
            f"缺失文件：{', '.join(result.missing)}\n空文件：{', '.join(result.empty)}\n"
            f"只允许生成或覆盖以下路径：\n{chr(10).join(allowed_paths)}\n\n上下文：\n{context}"
        ),
        config=config,
        metrics=metrics,
    )
    _materialize_files(workspace_dir, payload, allowed_paths=tuple(allowed_paths))


def _allowed_stage_repair_paths(workspace_dir: Path, expected_outputs: tuple[str, ...]) -> list[str]:
    paths: list[str] = []
    for expected in expected_outputs:
        if expected.endswith("/"):
            existing = [str(item.relative_to(workspace_dir)) for item in sorted((workspace_dir / expected).glob("*.md"))]
            paths.extend(existing or [f"{expected}首页.md"])
        elif "*" in expected:
            paths.extend(str(item.relative_to(workspace_dir)) for item in sorted(workspace_dir.glob(expected)))
        else:
            paths.append(expected)
    return sorted(dict.fromkeys(paths))


def _write_generation_report(workspace_dir: Path, contract: PrototypeContract, metrics: dict) -> None:
    files = _collect_existing_outputs(workspace_dir, PROTOTYPE_OUTPUTS)
    diagnostics = diagnose_llm_config()
    content = [
        "# 生成报告",
        "",
        f"系统名称：{contract.system_name}",
        f"页面数量：{len(contract.pages)}",
        f"菜单数量：{len(contract.menus)}",
        f"LLM 模型：{diagnostics.model}",
        f"LLM 调用次数：{metrics.get('llm_calls', 0)}",
        f"修复轮次：{metrics.get('repair_attempts', 0)}",
        f"生成耗时秒：{metrics.get('duration_seconds', 0)}",
        f"Skill 根目录：{skills_root()}",
        f"环境文件：{diagnostics.env_path}",
        f"Base URL 已配置：{'是' if diagnostics.base_url_configured else '否'}",
        "",
        "## 运行诊断",
        *(["- 无阻塞问题"] if not diagnostics.issues else [f"- 阻塞：{item}" for item in diagnostics.issues]),
        *(["- 无警告"] if not diagnostics.warnings else [f"- 警告：{item}" for item in diagnostics.warnings]),
        "",
        "## 页面清单",
        *[f"- {page.page_name}: {page.html_path}" for page in contract.pages],
        "",
        "## 实际文件清单",
        *[f"- {item}" for item in files],
    ]
    (workspace_dir / "generation-report.md").write_text("\n".join(content), encoding="utf-8")


def _write_validation_report(workspace_dir: Path, validation: ValidationResult) -> None:
    conclusion = "通过" if validation.ok else "不通过"
    missing = [f"- {item}" for item in validation.missing] or ["- 无"]
    empty = [f"- {item}" for item in validation.empty] or ["- 无"]
    issues = [f"- {item}" for item in validation.issues] or ["- 无"]
    warnings = [f"- {item}" for item in validation.warnings] or ["- 无"]
    content = [
        "# 校验报告",
        "",
        f"验收结论：{conclusion}",
        "",
        "## 缺失文件",
        *missing,
        "",
        "## 空文件",
        *empty,
        "",
        "## 阻塞问题",
        *issues,
        "",
        "## 警告",
        *warnings,
    ]
    (workspace_dir / "validation-report.md").write_text("\n".join(content), encoding="utf-8")


def _strip_code_fence(content: str) -> str:
    stripped = content.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _page_design_texts(workspace_dir: Path) -> dict[str, str]:
    page_dir = workspace_dir / "页面详细设计"
    if not page_dir.exists():
        return {}
    return {item.stem: item.read_text(encoding="utf-8") for item in sorted(page_dir.glob("*.md"))}


def _route_row_for_page(rows: list[dict[str, str]], page_name: str) -> dict[str, str] | None:
    for row in rows:
        value = normalize_page_name(_find_row_value(row, "页面名称", "页面", "菜单名称", "菜单"))
        if value == page_name:
            return row
    return None


def _find_row_value(row: dict[str, str] | None, *keys: str) -> str:
    if not row:
        return ""
    for key in keys:
        if key in row and row[key].strip():
            return row[key].strip()
    for actual_key, value in row.items():
        if any(key in actual_key for key in keys) and value.strip():
            return value.strip()
    return ""


def _split_contract_values(value: str) -> list[str]:
    if not value:
        return []
    parts = re.split(r"[,，、;；/]|\s+", value)
    return [item.strip() for item in parts if item.strip() and item.strip() != "-"][:8]


def _links_for_page(page_name: str, page_names: list[str], row: dict[str, str] | None) -> list[str]:
    links = [page_href_for_page(page_name)]
    raw = _find_row_value(row, "跳转关系", "跳转") if row else ""
    for candidate in page_names:
        if candidate != page_name and (candidate in raw or not raw):
            links.append(page_href_for_page(candidate))
    if len(links) == 1 and page_names:
        links.append(page_href_for_page(page_names[0]))
    return list(dict.fromkeys(links))


def _required_sections(page_name: str, page_design: str, features: list[str]) -> list[str]:
    sections = [page_name, "页面标题", "主导航"]
    sections.extend(features[:4])
    if any(token in page_name for token in ("列表", "管理", "查询")):
        sections.extend(["筛选", "列表", "操作"])
    if any(token in page_name for token in ("详情", "明细")):
        sections.extend(["详情", "关联记录", "返回"])
    if any(token in page_name for token in ("新增", "编辑", "创建")):
        sections.extend(["表单", "保存", "取消"])
    if any(token in page_name for token in ("统计", "报表", "看板", "工作台", "首页")):
        sections.extend(["指标", "趋势", "待办"])
    for token in re.findall(r"(?:组件|区块|模块)[:：]\s*([^\n]+)", page_design):
        sections.extend(_split_contract_values(token))
    return tuple(dict.fromkeys(item for item in sections if item))[:12]


def _primary_actions(page_design: str, features: list[str]) -> list[str]:
    actions = []
    for token in re.findall(r"(?:操作|按钮|动作)[:：]\s*([^\n]+)", page_design):
        actions.extend(_split_contract_values(token))
    actions.extend(feature for feature in features if any(word in feature for word in ("新增", "编辑", "删除", "审核", "保存", "导出", "分配", "跟进")))
    return list(dict.fromkeys(actions or ["查看", "提交", "返回"]))[:8]


def _infer_page_type(page_name: str, page_design: str) -> str:
    text = page_name + page_design
    if any(token in text for token in ("详情", "明细")):
        return "详情页"
    if any(token in text for token in ("新增", "编辑", "创建", "表单")):
        return "表单页"
    if any(token in text for token in ("统计", "报表", "看板", "工作台")):
        return "看板页"
    if any(token in text for token in ("列表", "管理", "查询")):
        return "列表页"
    return "业务页"


def _infer_data_entities(pages: list[PageContract], source: str) -> list[DataEntityContract]:
    entities: list[DataEntityContract] = [
        DataEntityContract("用户", "users", ("id", "name", "role", "department"), used_by_pages=tuple(page.page_name for page in pages)),
        DataEntityContract("角色", "roles", ("id", "name", "permissions"), used_by_pages=tuple(page.page_name for page in pages)),
        DataEntityContract("导航菜单", "navMenus", ("key", "label", "href", "order"), used_by_pages=tuple(page.page_name for page in pages)),
    ]
    domain_map = (
        ("客户", "customers", ("id", "name", "status", "ownerId", "updatedAt")),
        ("线索", "leads", ("id", "name", "status", "source", "ownerId")),
        ("跟进", "followRecords", ("id", "businessId", "content", "nextTime", "ownerId")),
        ("订单", "orders", ("id", "customerId", "status", "amount", "createdAt")),
        ("任务", "tasks", ("id", "title", "status", "assigneeId", "dueAt")),
        ("通知", "notifications", ("id", "title", "read", "createdAt")),
    )
    for keyword, js_key, fields in domain_map:
        used_pages = tuple(page.page_name for page in pages if keyword in page.page_name or keyword in " ".join(page.feature_names) or keyword in source)
        if used_pages:
            entities.append(DataEntityContract(keyword, js_key, fields, used_by_pages=used_pages))
    return entities


def _infer_system_name(requirement: str) -> str:
    match = re.search(r"([^，。\n]{2,30}?系统)", requirement)
    return match.group(1) if match else "业务原型系统"


def _contract_key(value: str | None) -> str:
    value = normalize_page_name(value or "nav")
    return re.sub(r"\W+", "-", value).strip("-") or "nav"


def _dedupe_menu_items(items: list[MenuItemContract]) -> tuple[MenuItemContract, ...]:
    seen: set[str] = set()
    deduped: list[MenuItemContract] = []
    for item in items:
        identity = item.key or item.label
        if identity in seen:
            continue
        seen.add(identity)
        deduped.append(item)
    return tuple(deduped)


def fail_node(state: WorkflowState) -> dict:
    failures = [item for item in state.get("validations", []) if not item.ok]
    if not failures:
        return {"status": "failed", "error_message": state.get("error_message") or "workflow failed"}
    latest = failures[-1]
    details = []
    if latest.missing:
        details.append("missing: " + ", ".join(latest.missing))
    if latest.empty:
        details.append("empty: " + ", ".join(latest.empty))
    if latest.issues:
        details.append("issues: " + "; ".join(latest.issues[:5]))
    return {"status": "failed", "error_message": f"{latest.stage} validation failed ({'; '.join(details)})"}


def route_after_validation(state: WorkflowState) -> str:
    validations = state.get("validations", [])
    if validations and validations[-1].ok:
        return "ok"
    return "failed"


def _validation_update(result) -> dict:
    update = {"validations": [result]}
    if not result.ok:
        detail = "; ".join(result.issues[:3]) if result.issues else ""
        update["error_message"] = f"{result.stage} validation failed" + (f": {detail}" if detail else "")
    return update
