from pathlib import Path


class LocalStorage:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def build_project_paths(self, project_id: str) -> dict:
        current = self.base_path / "projects" / project_id / "current"
        runs = self.base_path / "projects" / project_id / "runs"
        current.mkdir(parents=True, exist_ok=True)
        runs.mkdir(parents=True, exist_ok=True)
        return {
            "current": str(current),
            "runs": str(runs),
        }
