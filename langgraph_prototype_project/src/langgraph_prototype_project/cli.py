from __future__ import annotations

import argparse
import sys
from pathlib import Path

from langgraph_prototype_project.llm import diagnose_llm_config
from langgraph_prototype_project.skills import skill_file_path, skills_root
from langgraph_prototype_project.workflow import repair_existing_workflow, run_workflow


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the LangGraph requirement-to-prototype workflow.")
    parser.add_argument("requirement", nargs="?", help="Raw requirement text. If omitted, stdin is used.")
    parser.add_argument("--output-dir", default="langgraph_prototype_project/runs", help="Directory for workflow outputs.")
    parser.add_argument("--parallel-workers", type=int, default=4, help="Max concurrent prototype page writers.")
    parser.add_argument("--resume-workspace", help="Existing run workspace to repair from prototype validation onward.")
    parser.add_argument("--check", action="store_true", help="Check runtime configuration without calling the LLM.")
    args = parser.parse_args()

    if args.check:
        return _run_preflight_check(Path(args.output_dir), Path(args.resume_workspace) if args.resume_workspace else None)

    requirement = args.requirement or sys.stdin.read().strip()
    if not requirement:
        parser.error("requirement text is required")

    if args.resume_workspace:
        result = repair_existing_workflow(requirement, Path(args.resume_workspace), parallel_workers=args.parallel_workers)
    else:
        result = run_workflow(requirement, Path(args.output_dir), parallel_workers=args.parallel_workers)
    print(f"status={result.status}")
    print(f"workspace={result.workspace_dir}")
    if result.prototype_dir:
        print(f"prototype={result.prototype_dir}")
    print(f"artifacts={len(result.artifacts)}")
    if result.error_message:
        print(f"error={result.error_message}")
    return 0 if result.status == "success" else 1


def _run_preflight_check(output_dir: Path, resume_workspace: Path | None) -> int:
    diagnostics = diagnose_llm_config()
    issues = list(diagnostics.issues)
    warnings = list(diagnostics.warnings)
    required_skills = ("requirement-intake-structuring", "system-function-design-planning", "prototype-generator")
    root = skills_root()

    if resume_workspace and not resume_workspace.exists():
        issues.append(f"resume workspace not found: {resume_workspace}")
    if not output_dir.exists():
        warnings.append(f"output dir will be created: {output_dir}")
    for skill_name in required_skills:
        path = skill_file_path(skill_name)
        if not path.is_file():
            issues.append(f"skill not found: {path}")

    print("preflight=ok" if not issues else "preflight=failed")
    print(f"env={diagnostics.env_path}")
    print(f"model={diagnostics.model}")
    print(f"api_key_present={str(diagnostics.api_key_present).lower()}")
    print(f"base_url_configured={str(diagnostics.base_url_configured).lower()}")
    print(f"timeout={diagnostics.timeout if diagnostics.timeout is not None else 'invalid'}")
    print(f"skills_root={root}")
    print(f"output_dir={output_dir}")
    if resume_workspace:
        print(f"resume_workspace={resume_workspace}")
    for warning in warnings:
        print(f"warning={warning}")
    for issue in issues:
        print(f"issue={issue}")
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
