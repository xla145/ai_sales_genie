from __future__ import annotations

import re


_PAGE_HINTS = ("页面", "模块", "功能", "菜单", "路由")


def extract_pages(requirement: str, limit: int = 20) -> list[str]:
    pages: list[str] = []
    candidates = re.findall(r"(?:页面|模块|功能|菜单|路由)[:：]\s*([^\n]+)", requirement)
    for candidate in candidates:
        pages.extend(_split_page_names(candidate))

    for line in requirement.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        list_match = re.match(r"^(?:[-*]|\d+[.、)]|[（(]?\d+[）)])\s*(.+)$", stripped)
        if list_match and any(hint in stripped for hint in _PAGE_HINTS):
            pages.extend(_split_page_names(list_match.group(1)))

    return dedupe_pages(pages)[:limit] or ["首页"]


def dedupe_pages(pages: list[str] | tuple[str, ...]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for page in pages:
        name = normalize_page_name(page)
        if not name or name in seen:
            continue
        seen.add(name)
        normalized.append(name)
    return normalized


def normalize_page_name(name: str) -> str:
    name = re.sub(r"[`*_#>\[\]()（）]", "", name).strip(" ，,、。；;：:")
    name = re.sub(r"^(?:页面|模块|功能|菜单|路由)\s*[:：-]?\s*", "", name)
    name = re.sub(r"\s+", "", name)
    return name[:40]


def page_name_to_filename(name: str) -> str:
    filename = slugify(normalize_page_name(name))
    return f"{filename}.html"


def html_path_for_page(name: str) -> str:
    return f"prototype/pages/{page_name_to_filename(name)}"


def page_href_for_page(name: str) -> str:
    return f"./{page_name_to_filename(name)}"


def parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|") and line.strip().endswith("|")]
    index = 0
    while index < len(lines):
        header = _split_table_row(lines[index])
        if index + 1 >= len(lines) or not _is_separator_row(lines[index + 1]):
            index += 1
            continue
        index += 2
        while index < len(lines):
            cells = _split_table_row(lines[index])
            if len(cells) != len(header):
                break
            rows.append({header[i]: cells[i] for i in range(len(header))})
            index += 1
    return rows


def extract_route_rows(markdown: str) -> list[dict[str, str]]:
    route_rows: list[dict[str, str]] = []
    for row in parse_markdown_table(markdown):
        joined_keys = " ".join(row.keys())
        if any(token in joined_keys for token in ("页面", "路由", "菜单", "文件")):
            if any(_row_value(row, key) for key in ("页面", "页面名称", "菜单", "菜单名称", "路由", "路径", "文件")):
                route_rows.append(row)
    return route_rows


def _row_value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        if key in row and row[key].strip():
            return row[key].strip()
    for actual_key, value in row.items():
        if any(key in actual_key for key in keys) and value.strip():
            return value.strip()
    return ""


def _split_page_names(text: str) -> list[str]:
    text = re.sub(r"[。；;]", "、", text)
    parts = re.split(r"[,，、/]|\s+和\s+|\s+及\s+", text)
    return [normalize_page_name(part) for part in parts if normalize_page_name(part)]


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    cells = _split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def slugify(name: str) -> str:
    slug = re.sub(r"\s+", "-", name.strip())
    slug = slug.replace("/", "-").replace("\\", "-")
    slug = re.sub(r"[<>:\"|?*]", "-", slug)
    return slug or "page"
