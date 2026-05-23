#!/usr/bin/env python3
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional


PHASES = [
    {
        "key": "phase1",
        "title": "阶段一：需求结构化",
        "run_type": "phase1_requirement",
        "user_message": "生成阶段一：需求结构化",
        "instruction": "生成第一个阶段：需求结构化。必须输出 `需求结构化.md`。",
    },
    {
        "key": "phase2",
        "title": "阶段二：功能与页面设计",
        "run_type": "phase2_design",
        "user_message": "进入阶段二：功能与页面设计",
        "instruction": (
            "进入阶段二：PRD 与功能点设计。基于当前 workspace 中的需求结构化产物，"
            "只输出最终产物 `PRD.md` 和 `系统的功能点设计.md`；"
            "不要输出页面详细设计、检查报告或其他中间产物。"
        ),
    },
    {
        "key": "phase3",
        "title": "阶段三：原型生成",
        "run_type": "phase3_prototype",
        "user_message": "进入阶段三：原型生成",
        "instruction": (
            "进入阶段三：原型生成。基于当前 workspace 中的 PRD 和功能点最终产物，"
            "只输出 `prototype/` 多页面静态原型文件；不要输出 generation-report、validation-report 或其他中间产物。"
        ),
    },
]


def request_json(method: str, url: str, body: Optional[dict] = None, timeout: int = 1200):
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else {}
            return resp.status, parsed
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {"raw": raw}
        except Exception:
            parsed = {"raw": raw}
        return e.code, parsed


def request_bytes(url: str, timeout: int = 120):
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def print_step(title: str, status: int, payload):
    print(f"\n=== {title} ===")
    print(f"status: {status}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return slug.strip("_") or "run"


def make_run_id(prefix: str, phase_key: str, timestamp: str, reuse_fixed_run_ids: bool) -> str:
    clean_prefix = slugify(prefix)
    if reuse_fixed_run_ids:
        return f"{clean_prefix}_{phase_key}"
    return f"{clean_prefix}_{phase_key}_{timestamp}"


def ensure_project(base: str, project_id: str, project_name: str, requirement_file: Path) -> None:
    project_payload = {
        "project_id": project_id,
        "name": project_name,
        "description": f"source={requirement_file}",
    }
    status, body = request_json("POST", f"{base}/projects", project_payload, timeout=30)
    print_step("project:create", status, body)
    if status == 409:
        get_status, get_body = request_json("GET", f"{base}/projects/{project_id}", None, timeout=30)
        print_step("project:get", get_status, get_body)
        if get_status != 200:
            sys.exit(3)
        return
    if status != 200:
        sys.exit(3)


def create_run(base: str, *, run_id: str, project_id: str, session_id: str, run_type: str, user_message: str) -> None:
    run_payload = {
        "run_id": run_id,
        "project_id": project_id,
        "session_id": session_id,
        "run_type": run_type,
        "user_message": user_message,
    }
    status, body = request_json("POST", f"{base}/runs", run_payload, timeout=30)
    print_step(f"run:create:{run_id}", status, body)
    if status == 409:
        print(f"run_id already exists, skip executing old run: {run_id}")
        sys.exit(4)
    if status != 200:
        sys.exit(4)


def download_artifacts(base: str, run_id: str, output_root: Path) -> list[dict]:
    status, body = request_json("GET", f"{base}/runs/{run_id}/artifacts", None, timeout=30)
    print_step(f"artifacts:list:{run_id}", status, body)
    if status != 200:
        return []

    saved = []
    artifacts = body.get("artifacts", []) if isinstance(body, dict) else []
    out_dir = output_root / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in artifacts:
        artifact_id = item.get("artifact_id")
        name = item.get("name") or f"artifact_{artifact_id}"
        if not artifact_id:
            continue
        url = f"{base}/runs/{run_id}/artifacts/{artifact_id}"
        try:
            download_status, data = request_bytes(url, timeout=120)
            target = out_dir / name
            target.write_bytes(data)
            saved.append({"artifact_id": artifact_id, "name": name, "status": download_status, "saved_to": str(target)})
        except Exception as exc:
            saved.append({"artifact_id": artifact_id, "name": name, "error": repr(exc)})

    print(f"\n=== artifacts:download:{run_id} ===")
    print(json.dumps(saved, ensure_ascii=False, indent=2))
    return saved


def execute_phase(
    base: str,
    *,
    project_id: str,
    session_id: str,
    run_id: str,
    phase: dict,
    requirement_text: str,
    timeout: int,
    output_root: Path,
) -> dict:
    create_run(
        base,
        run_id=run_id,
        project_id=project_id,
        session_id=session_id,
        run_type=phase["run_type"],
        user_message=phase["user_message"],
    )

    if phase["key"] == "phase1":
        prompt = f"{requirement_text}\n\n{phase['instruction']}"
    else:
        prompt = phase["instruction"]

    execute_payload = {
        "project_id": project_id,
        "prompt": prompt,
    }
    execute_status, execute_body = request_json(
        "POST",
        f"{base}/runs/{run_id}/execute",
        execute_payload,
        timeout=timeout + 300,
    )
    print_step(f"run:execute:{run_id}", execute_status, execute_body)

    run_status, run_body = request_json("GET", f"{base}/runs/{run_id}", None, timeout=30)
    print_step(f"run:get:{run_id}", run_status, run_body)

    events_status, events_body = request_json("GET", f"{base}/events/{run_id}?after_id=0&limit=500", None, timeout=30)
    print_step(f"events:list:{run_id}", events_status, events_body)

    saved = download_artifacts(base, run_id, output_root)
    generated_files = execute_body.get("generated_files", []) if isinstance(execute_body, dict) else []

    return {
        "phase": phase["key"],
        "title": phase["title"],
        "run_id": run_id,
        "execute_status": execute_status,
        "run_status": run_body.get("status") if isinstance(run_body, dict) else None,
        "generated_files": generated_files,
        "artifact_download_dir": str(output_root / run_id),
        "downloaded_count": len([item for item in saved if item.get("saved_to")]),
    }


def main():
    parser = argparse.ArgumentParser(description="Run prototype generation flow with repeated project/session runs")
    parser.add_argument("--base", default="http://127.0.0.1:8081", help="API base URL")
    parser.add_argument("--requirement", default="/Users/mac/xula/ai_sales_genie/原始需求.md", help="Requirement markdown path")
    parser.add_argument("--project-id", default="proj_rawreq_flow", help="Stable project id; reuse it for continuous changes/questions")
    parser.add_argument("--project-name", default="原始需求验证项目")
    parser.add_argument("--session-id", default="sess_rawreq_flow", help="Stable session id for the same conversation/project flow")
    parser.add_argument("--run-prefix", default="run_rawreq_flow", help="Run id prefix; each phase appends phase key and timestamp")
    parser.add_argument("--phase", choices=["all", "phase1", "phase2", "phase3"], default="all")
    parser.add_argument("--modify-prototype", help="Create a new prototype version from the current version using this change request")
    parser.add_argument("--reuse-fixed-run-ids", action="store_true", help="Use deterministic run ids; useful only after clearing existing runs")
    parser.add_argument("--poll-timeout", type=int, default=1800)
    args = parser.parse_args()

    base = args.base.rstrip("/")
    requirement_file = Path(args.requirement)
    if not requirement_file.is_file():
        print(f"requirement file not found: {requirement_file}")
        sys.exit(1)

    requirement_text = requirement_file.read_text(encoding="utf-8")
    health_status, health_body = request_json("GET", f"{base}/health", None, timeout=10)
    print_step("health", health_status, health_body)
    if health_status != 200:
        sys.exit(2)

    ensure_project(base, args.project_id, args.project_name, requirement_file)

    timestamp = time.strftime("%Y%m%d%H%M%S")
    if args.modify_prototype:
        selected_phases = [
            {
                "key": "prototype_edit",
                "title": "原型修改",
                "run_type": "prototype_edit",
                "user_message": args.modify_prototype,
                "instruction": (
                    "修改当前原型并生成一个新的完整原型版本。"
                    "只返回需要变更的 `prototype/` 文件；不要返回中间文档。\n\n"
                    f"修改要求：{args.modify_prototype}"
                ),
            }
        ]
    else:
        selected_phases = PHASES if args.phase == "all" else [phase for phase in PHASES if phase["key"] == args.phase]
    output_root = Path.cwd() / "artifact_downloads" / args.project_id / timestamp
    summaries = []

    for phase in selected_phases:
        run_id = make_run_id(args.run_prefix, phase["key"], timestamp, args.reuse_fixed_run_ids)
        summaries.append(
            execute_phase(
                base,
                project_id=args.project_id,
                session_id=args.session_id,
                run_id=run_id,
                phase=phase,
                requirement_text=requirement_text,
                timeout=args.poll_timeout,
                output_root=output_root,
            )
        )

    summary = {
        "base": base,
        "requirement": str(requirement_file),
        "project_id": args.project_id,
        "session_id": args.session_id,
        "phase": "prototype_edit" if args.modify_prototype else args.phase,
        "artifact_download_root": str(output_root),
        "runs": summaries,
    }
    print("\n=== summary ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
