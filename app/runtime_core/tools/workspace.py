from __future__ import annotations

from pathlib import Path

from app.runtime_core.tools.base import ToolRiskLevel, ToolSpec


def build_workspace_tools(workspace_dir: Path) -> list[ToolSpec]:
    return [
        ToolSpec(
            name="read_file",
            description="Read a UTF-8 file from the current workspace.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1},
                },
                "required": ["path"],
            },
            handler=lambda path, limit=None: _read_file(workspace_dir, path, limit=limit),
            risk_level=ToolRiskLevel.SAFE,
        ),
        ToolSpec(
            name="write_file",
            description="Write a UTF-8 file into the current workspace.",
            parameters_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
            handler=lambda path, content: _write_file(workspace_dir, path, content),
            risk_level=ToolRiskLevel.WRITE,
        ),
        ToolSpec(
            name="list_files",
            description="List files under the current workspace or a relative subdirectory.",
            parameters_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
            handler=lambda path=".": _list_files(workspace_dir, path),
            risk_level=ToolRiskLevel.SAFE,
        ),
        ToolSpec(
            name="delete_file",
            description="Delete a file from the current workspace.",
            parameters_schema={
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
            handler=lambda path: _delete_file(workspace_dir, path),
            risk_level=ToolRiskLevel.WRITE,
        ),
    ]


def _read_file(workspace_dir: Path, relative_path: str, limit: int | None = None) -> str:
    path = _resolve_workspace_path(workspace_dir, relative_path)
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    if isinstance(limit, int) and limit > 0:
        return "\n".join(content.splitlines()[:limit])
    return content


def _write_file(workspace_dir: Path, relative_path: str, content: str) -> str:
    path = _resolve_workspace_path(workspace_dir, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return f"wrote:{path.relative_to(workspace_dir.resolve())}"


def _list_files(workspace_dir: Path, relative_path: str = ".") -> str:
    target = _resolve_workspace_path(workspace_dir, relative_path)
    if target.is_file():
        return str(target.relative_to(workspace_dir.resolve()))
    files = sorted(str(item.relative_to(workspace_dir.resolve())) for item in target.rglob("*") if item.is_file())
    return "\n".join(files)


def _delete_file(workspace_dir: Path, relative_path: str) -> str:
    path = _resolve_workspace_path(workspace_dir, relative_path)
    if path.exists() and path.is_file():
        path.unlink()
        return f"deleted:{path.relative_to(workspace_dir.resolve())}"
    return "deleted:"


def _resolve_workspace_path(workspace_dir: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    workspace_root = workspace_dir.resolve()
    if candidate.is_absolute():
        if candidate.resolve() == workspace_root:
            return workspace_root
        raise ValueError(f"Absolute path is not allowed: {relative_path}")
    normalized = (workspace_dir / candidate).resolve()
    if normalized != workspace_root and workspace_root not in normalized.parents:
        raise ValueError(f"Path escapes workspace: {relative_path}")
    return normalized
