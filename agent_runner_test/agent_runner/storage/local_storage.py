import json
import shutil
from pathlib import Path


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def build_project_paths(self, project_id: str) -> dict:
        project_root = self.base_path / "projects" / project_id
        deliverables = project_root / "deliverables"
        current = deliverables / "current"
        prototypes = deliverables / "prototypes"
        runs = project_root / "runs"
        current.mkdir(parents=True, exist_ok=True)
        prototypes.mkdir(parents=True, exist_ok=True)
        runs.mkdir(parents=True, exist_ok=True)
        return {
            "project_root": str(project_root),
            "deliverables": str(deliverables),
            "current": str(current),
            "prototypes": str(prototypes),
            "runs": str(runs),
            "version_file": str(deliverables / "current_version.json"),
        }

    def read_current_version(self, project_id: str) -> dict:
        paths = self.build_project_paths(project_id)
        version_file = Path(paths["version_file"])
        if not version_file.is_file():
            return {"current_prototype_version": None, "versions": []}
        try:
            data = json.loads(version_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"current_prototype_version": None, "versions": []}
        if not isinstance(data, dict):
            return {"current_prototype_version": None, "versions": []}
        data.setdefault("current_prototype_version", None)
        data.setdefault("versions", [])
        return data

    def write_current_version(self, project_id: str, data: dict) -> None:
        paths = self.build_project_paths(project_id)
        version_file = Path(paths["version_file"])
        version_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_next_prototype_version(self, project_id: str, *, run_id: str, user_instruction: str) -> dict:
        paths = self.build_project_paths(project_id)
        version_state = self.read_current_version(project_id)
        versions = version_state.get("versions") if isinstance(version_state.get("versions"), list) else []
        base_version = version_state.get("current_prototype_version")
        next_number = len(versions) + 1
        version_name = f"v{next_number}"
        prototypes_dir = Path(paths["prototypes"])
        target_dir = prototypes_dir / version_name

        if isinstance(base_version, str) and base_version:
            base_dir = prototypes_dir / base_version
            if base_dir.is_dir() and not target_dir.exists():
                shutil.copytree(base_dir, target_dir)
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir.mkdir(parents=True, exist_ok=True)

        entry = {
            "version": version_name,
            "version_number": next_number,
            "base_version": base_version,
            "run_id": run_id,
            "user_instruction": user_instruction,
            "storage_path": str(target_dir),
            "status": "pending",
        }
        versions.append(entry)
        version_state["versions"] = versions
        self.write_current_version(project_id, version_state)
        return entry

    def finalize_prototype_version(self, project_id: str, version: str) -> dict:
        version_state = self.read_current_version(project_id)
        versions = version_state.get("versions") if isinstance(version_state.get("versions"), list) else []
        for item in versions:
            if isinstance(item, dict) and item.get("version") == version:
                item["status"] = "success"
                version_state["current_prototype_version"] = version
                break
        version_state["versions"] = versions
        self.write_current_version(project_id, version_state)
        return version_state
