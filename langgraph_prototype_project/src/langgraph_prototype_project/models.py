from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict
import operator


StageName = Literal["requirement_intake", "system_design", "prototype_generation"]
WorkflowStatus = Literal["pending", "running", "success", "failed"]


@dataclass(frozen=True)
class ValidationResult:
    stage: str
    ok: bool
    missing: tuple[str, ...] = ()
    empty: tuple[str, ...] = ()
    issues: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkflowResult:
    status: WorkflowStatus
    workspace_dir: Path
    prototype_dir: Path | None
    artifacts: tuple[str, ...]
    validations: tuple[ValidationResult, ...]
    error_message: str | None = None


@dataclass(frozen=True)
class MenuItemContract:
    key: str
    label: str
    href: str
    order: int
    page_name: str
    parent_key: str | None = None


@dataclass(frozen=True)
class PageContract:
    page_name: str
    file_name: str
    html_path: str
    page_type: str = "业务页"
    module_name: str = "核心业务"
    parent_menu: str | None = None
    feature_names: tuple[str, ...] = ()
    primary_actions: tuple[str, ...] = ()
    allowed_links: tuple[str, ...] = ()
    required_sections: tuple[str, ...] = ()
    current_nav_key: str | None = None


@dataclass(frozen=True)
class DataEntityContract:
    entity_name: str
    js_key: str
    fields: tuple[str, ...] = ()
    relations: tuple[str, ...] = ()
    used_by_pages: tuple[str, ...] = ()


@dataclass(frozen=True)
class PrototypeContract:
    system_name: str
    pages: tuple[PageContract, ...]
    menus: tuple[MenuItemContract, ...]
    data_entities: tuple[DataEntityContract, ...] = ()
    js_api: tuple[str, ...] = (
        "showToast",
        "openModal",
        "closeModal",
        "validateRequired",
        "submitWithLoading",
        "toggleSidebar",
        "getCurrentUser",
        "setCurrentNav",
    )
    shared_components: tuple[str, ...] = (
        "app-shell",
        "sidebar",
        "topbar",
        "nav-link",
        "page-header",
        "stat-card",
        "data-table",
        "filter-bar",
        "form-grid",
        "status-badge",
        "modal",
        "empty-state",
        "toast",
    )
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def page_names(self) -> tuple[str, ...]:
        return tuple(page.page_name for page in self.pages)

    @property
    def page_paths(self) -> tuple[str, ...]:
        return tuple(page.html_path for page in self.pages)


class WorkflowState(TypedDict, total=False):
    requirement: str
    workspace_dir: str
    status: WorkflowStatus
    current_stage: StageName
    error_message: str | None
    artifacts: list[str]
    validations: Annotated[list[ValidationResult], operator.add]
    pages: list[str]
    prototype_dir: str | None
    parallel_workers: int
    use_llm: bool
    llm_model: str | None
    llm_config: Any
    prototype_contract: PrototypeContract | None
    generation_metrics: dict[str, Any]
