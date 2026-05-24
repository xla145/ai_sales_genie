from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from langgraph_prototype_project.models import PrototypeContract, ValidationResult
from langgraph_prototype_project.utils import page_href_for_page, page_name_to_filename


REQUIREMENT_OUTPUTS = ("需求结构化.md",)
SYSTEM_DESIGN_OUTPUTS = (
    "系统全局功能描述与设计.md",
    "系统的功能点设计.md",
    "页面详细设计/",
    "第二阶段设计检查报告.md",
)
PROTOTYPE_OUTPUTS = (
    "prototype/index.html",
    "prototype/README.md",
    "prototype/assets/css/styles.css",
    "prototype/assets/js/app.js",
    "prototype/assets/js/mock-data.js",
    "prototype/pages/*.html",
    "generation-report.md",
    "validation-report.md",
)

_BLOCKING_REPORT_TERMS = ("不通过", "未通过", "失败", "failed", "fail")
_PLACEHOLDER_TERMS = ("功能开发中", "待开发", "敬请期待", "需跳转到详情页", "需跳转到新增页面")
_GLOBAL_FUNCTIONS = (
    "showToast",
    "openModal",
    "closeModal",
    "validateRequired",
    "submitWithLoading",
    "toggleSidebar",
    "getCurrentUser",
    "setCurrentNav",
)


def validate_outputs(workspace_dir: Path, stage: str, expected_outputs: tuple[str, ...]) -> ValidationResult:
    missing: list[str] = []
    empty: list[str] = []

    for relative_path in expected_outputs:
        if "*" in relative_path:
            matches = sorted(workspace_dir.glob(relative_path))
            if not matches:
                missing.append(relative_path)
                continue
            empty.extend(str(path.relative_to(workspace_dir)) for path in matches if path.is_file() and path.stat().st_size == 0)
            continue

        path = workspace_dir / relative_path
        if not path.exists():
            missing.append(relative_path)
            continue
        if path.is_file() and path.stat().st_size == 0:
            empty.append(relative_path)
        if path.is_dir() and not any(path.iterdir()):
            empty.append(relative_path)

    return ValidationResult(stage=stage, ok=not missing and not empty, missing=tuple(missing), empty=tuple(empty))


def validate_prototype_semantics(workspace_dir: Path, expected_pages: list[str] | None = None, contract: PrototypeContract | None = None) -> ValidationResult:
    base = validate_outputs(workspace_dir, "prototype_generation", PROTOTYPE_OUTPUTS)
    issues = list(base.issues)
    warnings = list(base.warnings)
    prototype_dir = workspace_dir / "prototype"
    pages = list(contract.page_names) if contract else (expected_pages or [])

    if prototype_dir.exists():
        _check_expected_pages(prototype_dir, pages, issues)
        _check_html_files(prototype_dir, issues, warnings, contract)
        _check_app_js(prototype_dir / "assets" / "js" / "app.js", issues, contract)
        _check_mock_data(prototype_dir / "assets" / "js" / "mock-data.js", pages, issues, warnings, contract)
    _check_reports(workspace_dir, issues)

    ok = not base.missing and not base.empty and not issues
    return ValidationResult(
        stage="prototype_generation",
        ok=ok,
        missing=base.missing,
        empty=base.empty,
        issues=tuple(dict.fromkeys(issues)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _check_expected_pages(prototype_dir: Path, expected_pages: list[str], issues: list[str]) -> None:
    if not expected_pages:
        return
    generated = {path.name for path in (prototype_dir / "pages").glob("*.html")}
    generated_stems = {path.stem for path in (prototype_dir / "pages").glob("*.html")}
    for page in expected_pages:
        expected_file = page_name_to_filename(page)
        if expected_file not in generated and page not in generated_stems:
            issues.append(f"expected page not generated: prototype/pages/{expected_file}")


def _check_html_files(prototype_dir: Path, issues: list[str], warnings: list[str], contract: PrototypeContract | None) -> None:
    html_files = [prototype_dir / "index.html", *sorted((prototype_dir / "pages").glob("*.html"))]
    for html_file in html_files:
        if not html_file.is_file():
            continue
        content = html_file.read_text(encoding="utf-8")
        _check_local_links(prototype_dir, html_file, content, issues)
        _check_asset_references(prototype_dir, html_file, content, issues)
        _check_static_navigation(prototype_dir, html_file, content, issues)
        _check_placeholder_actions(html_file, content, issues)
        _check_page_function_calls(html_file, content, prototype_dir / "assets" / "js" / "app.js", issues)
    if contract:
        _check_navigation_consistency(prototype_dir, contract, issues)
        _check_contract_links(prototype_dir, contract, issues)
        _check_page_content_completeness(prototype_dir, contract, issues, warnings)


def _check_local_links(prototype_dir: Path, html_file: Path, content: str, issues: list[str]) -> None:
    hrefs = re.findall(r"href=[\"']([^\"']+)[\"']", content, flags=re.I)
    for href in hrefs:
        target = _resolve_local_html(html_file, href)
        if target is None:
            continue
        if not target.exists():
            issues.append(f"broken local link in {html_file.relative_to(prototype_dir)}: {href}")


def _resolve_local_html(html_file: Path, href: str) -> Path | None:
    parsed = urlparse(href)
    if parsed.scheme in {"http", "https", "mailto", "tel", "javascript"}:
        return None
    if href.startswith("#"):
        return None
    path = unquote(parsed.path)
    if not path or not path.endswith(".html"):
        return None
    return (html_file.parent / path).resolve()


def _check_asset_references(prototype_dir: Path, html_file: Path, content: str, issues: list[str]) -> None:
    required = (
        ("./assets/css/styles.css", "./assets/js/mock-data.js", "./assets/js/app.js")
        if html_file.parent == prototype_dir
        else ("../assets/css/styles.css", "../assets/js/mock-data.js", "../assets/js/app.js")
    )
    for asset in required:
        if asset not in content:
            issues.append(f"missing required asset reference in {html_file.relative_to(prototype_dir)}: {asset}")


def _check_static_navigation(prototype_dir: Path, html_file: Path, content: str, issues: list[str]) -> None:
    if html_file.parent == prototype_dir:
        return
    local_page_links = [href for href in re.findall(r"href=[\"']([^\"']+\.html(?:\?[^\"']*)?)[\"']", content, flags=re.I)]
    has_nav_markup = any(token in content for token in ("<nav", "sidebar", "bottom-nav", "bottom-tab", "nav-link"))
    if not has_nav_markup or len(local_page_links) < 2:
        issues.append(f"business page lacks static navigation: {html_file.relative_to(prototype_dir)}")


def _check_placeholder_actions(html_file: Path, content: str, issues: list[str]) -> None:
    for term in _PLACEHOLDER_TERMS:
        if term in content:
            issues.append(f"placeholder core action in {html_file.name}: {term}")


def _check_page_function_calls(html_file: Path, content: str, app_js: Path, issues: list[str]) -> None:
    if not app_js.is_file():
        return
    app_content = app_js.read_text(encoding="utf-8")
    called = set(re.findall(r"(?:window\.)?(?:App\.)?([A-Za-z_][\w]*)\s*\(", content))
    for function_name in sorted(called.intersection(_GLOBAL_FUNCTIONS)):
        if not _function_exposed(app_content, function_name):
            issues.append(f"undefined global function used in {html_file.name}: {function_name}")


def _check_app_js(app_js: Path, issues: list[str], contract: PrototypeContract | None = None) -> None:
    if not app_js.is_file():
        return
    content = app_js.read_text(encoding="utf-8")
    required = contract.js_api if contract else ("showToast", "openModal", "closeModal", "toggleSidebar")
    for function_name in required:
        if function_name not in content or not _function_exposed(content, function_name):
            issues.append(f"app.js missing utility: {function_name}")


def _function_exposed(app_content: str, function_name: str) -> bool:
    patterns = (
        rf"window\.{re.escape(function_name)}\s*=",
        rf"window\.App\s*=\s*{{[^}}]*\b{re.escape(function_name)}\b",
        rf"App\.{re.escape(function_name)}\s*=",
        rf"window\.App\s*=\s*Object\.assign\([^)]*\b{re.escape(function_name)}\b",
    )
    return any(re.search(pattern, app_content, flags=re.S) for pattern in patterns)


def _check_mock_data(mock_data: Path, expected_pages: list[str], issues: list[str], warnings: list[str], contract: PrototypeContract | None = None) -> None:
    if not mock_data.is_file():
        return
    content = mock_data.read_text(encoding="utf-8")
    for token in ("window.MockData", "users", "roles"):
        if token not in content:
            issues.append(f"mock-data.js missing contract token: {token}")
    if "navMenus" not in content and "navigation" not in content:
        issues.append("mock-data.js missing navigation data")
    if contract:
        for entity in contract.data_entities:
            if entity.js_key not in content:
                issues.append(f"mock-data.js missing entity: {entity.js_key}")
                continue
            for field in entity.fields[:6]:
                if field and field not in content:
                    issues.append(f"mock-data.js missing field for {entity.js_key}: {field}")
    else:
        joined_pages = " ".join(expected_pages)
        domain_expectations = (("线索", "clue"), ("跟进", "follow"), ("客户", "customer"))
        for page_keyword, data_keyword in domain_expectations:
            if page_keyword in joined_pages and data_keyword.lower() not in content.lower():
                issues.append(f"mock-data.js missing domain data for pages containing {page_keyword}")
    if "notification" not in content.lower() and "todo" not in content.lower() and "通知" not in content:
        warnings.append("mock-data.js has limited notification/todo data")


def _check_navigation_consistency(prototype_dir: Path, contract: PrototypeContract, issues: list[str]) -> None:
    expected = [(menu.label, menu.href) for menu in sorted(contract.menus, key=lambda item: item.order)]
    if not expected:
        return
    for page in contract.pages:
        html_file = prototype_dir / "pages" / page.file_name
        if not html_file.is_file():
            continue
        content = html_file.read_text(encoding="utf-8")
        nav_content = _extract_nav_content(content)
        actual = _extract_nav_links(nav_content)
        for label, href in expected:
            if (label, href) not in actual:
                issues.append(f"navigation mismatch in pages/{page.file_name}: missing {label} -> {href}")
        actual_expected = [item for item in actual if item in expected]
        if actual_expected and actual_expected != expected[: len(actual_expected)]:
            issues.append(f"navigation order mismatch in pages/{page.file_name}")
        _check_active_navigation(page, nav_content, issues)


def _check_active_navigation(page, nav_content: str, issues: list[str]) -> None:
    active_links = re.findall(r"<a\b[^>]*(?:active|is-active|aria-current=[\"']page[\"'])[^>]*href=[\"']([^\"']+)[\"'][^>]*>", nav_content, flags=re.I | re.S)
    active_links += re.findall(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*(?:active|is-active|aria-current=[\"']page[\"'])[^>]*>", nav_content, flags=re.I | re.S)
    expected_hrefs = {page_href_for_page(page.page_name), page_href_for_page(page.parent_menu or page.page_name)}
    if not any(href in expected_hrefs for href in active_links):
        issues.append(f"navigation active state missing in pages/{page.file_name}")


def _check_contract_links(prototype_dir: Path, contract: PrototypeContract, issues: list[str]) -> None:
    all_page_hrefs = {page_href_for_page(page.page_name) for page in contract.pages}
    for page in contract.pages:
        html_file = prototype_dir / "pages" / page.file_name
        if not html_file.is_file():
            continue
        content = html_file.read_text(encoding="utf-8")
        allowed = set(page.allowed_links) | all_page_hrefs
        for href in re.findall(r"href=[\"']([^\"']+\.html(?:\?[^\"']*)?)[\"']", content, flags=re.I):
            clean_href = urlparse(href).path
            if clean_href not in allowed:
                issues.append(f"contract-external link in pages/{page.file_name}: {href}")


def _check_page_content_completeness(prototype_dir: Path, contract: PrototypeContract, issues: list[str], warnings: list[str]) -> None:
    for page in contract.pages:
        html_file = prototype_dir / "pages" / page.file_name
        if not html_file.is_file():
            continue
        content = re.sub(r"<[^>]+>", " ", html_file.read_text(encoding="utf-8"))
        if page.page_name not in content:
            issues.append(f"page title missing in pages/{page.file_name}: {page.page_name}")
        missing_sections = [section for section in page.required_sections if section and section not in content]
        if len(missing_sections) >= max(2, len(page.required_sections) // 2):
            issues.append(f"page content missing required sections in pages/{page.file_name}: {', '.join(missing_sections[:5])}")
        elif missing_sections:
            warnings.append(f"page content has limited section coverage in pages/{page.file_name}: {', '.join(missing_sections[:5])}")
        missing_actions = [action for action in page.primary_actions if action and action not in content]
        if len(missing_actions) >= 3:
            issues.append(f"page content missing primary actions in pages/{page.file_name}: {', '.join(missing_actions[:5])}")
        raw = html_file.read_text(encoding="utf-8")
        if page.page_type == "列表页" and not any(token in raw for token in ("<table", "data-table", "list", "列表", "卡片")):
            issues.append(f"list page lacks list/table content: pages/{page.file_name}")
        if page.page_type == "详情页" and not any(token in raw for token in ("详情", "detail", "字段", "关联")):
            issues.append(f"detail page lacks detail content: pages/{page.file_name}")
        if page.page_type == "表单页" and not any(token in raw for token in ("<input", "<select", "<textarea", "form-grid", "表单")):
            issues.append(f"form page lacks form controls: pages/{page.file_name}")


def _extract_nav_content(content: str) -> str:
    match = re.search(r"<nav\b[^>]*>(.*?)</nav>", content, flags=re.I | re.S)
    if match:
        return match.group(1)
    sidebar = re.search(r"<[^>]*(?:sidebar|bottom-nav|bottom-tab)[^>]*>(.*?)</[^>]+>", content, flags=re.I | re.S)
    return sidebar.group(1) if sidebar else content


def _extract_nav_links(content: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for href, label in re.findall(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", content, flags=re.I | re.S):
        if not href.endswith(".html"):
            continue
        text = re.sub(r"<[^>]+>", "", label).strip()
        if text:
            links.append((text, href))
    return links


def _check_reports(workspace_dir: Path, issues: list[str]) -> None:
    validation_report = workspace_dir / "validation-report.md"
    if validation_report.is_file():
        lines = validation_report.read_text(encoding="utf-8").splitlines()[:120]
        conclusion_lines = [line for line in lines if any(token in line for token in ("结论", "判定", "验收"))]
        scope = "\n".join(conclusion_lines or lines[:20]).lower()
        if any(term in scope for term in _BLOCKING_REPORT_TERMS):
            issues.append("validation-report.md final conclusion is not passing")

    generation_report = workspace_dir / "generation-report.md"
    if generation_report.is_file():
        content = generation_report.read_text(encoding="utf-8")
        for raw_path in re.findall(r"(?:prototype/)?pages/[\w\-.一-鿿]+\.html", content):
            relative = raw_path if raw_path.startswith("prototype/") else f"prototype/{raw_path}"
            if not (workspace_dir / relative).is_file():
                issues.append(f"generation-report.md references missing page: {relative}")
