import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.project import CreateProjectRequest, UpdateProjectRequest
from app.services.project_service import ProjectService
from app.storage.db_models import Base, UserRecord
from app.storage.header_store import InMemoryHeaderStore
from app.storage.sql_header_store import SqlHeaderStore


class ProjectAuditFieldsTest(unittest.TestCase):
    def test_project_create_and_update_sets_audit_user_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ProjectService(Path(temp_dir), header_store=InMemoryHeaderStore())

            project = service.create_project(CreateProjectRequest(name="Project A"), "user-1")

            self.assertEqual(project.created_id, "user-1")
            self.assertEqual(project.update_id, "user-1")

            project.update_id = "previous-user"
            service.save_project(project)

            updated = service.update_project(
                project.project_id,
                UpdateProjectRequest(name="Project A+", description="updated"),
                "user-1",
            )

            self.assertEqual(updated.created_id, "user-1")
            self.assertEqual(updated.update_id, "user-1")

    def test_project_retrieval_is_scoped_by_created_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            service = ProjectService(Path(temp_dir), header_store=InMemoryHeaderStore())
            owned = service.create_project(CreateProjectRequest(name="Owned"), "user-1")
            service.create_project(CreateProjectRequest(name="Other"), "user-2")

            projects = service.list_projects_for_user("user-1")

            self.assertEqual([project.project_id for project in projects], [owned.project_id])
            self.assertEqual(service.get_project_for_user(owned.project_id, "user-1").project_id, owned.project_id)
            with self.assertRaises(FileNotFoundError):
                service.get_project_for_user(owned.project_id, "user-2")

    def test_sql_project_retrieval_is_filtered_by_created_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            engine = create_engine(f"sqlite+pysqlite:///{Path(temp_dir) / 'test.db'}", future=True)
            Base.metadata.create_all(engine)
            session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
            now = datetime.now()
            with session_factory() as session:
                session.add_all([
                    UserRecord(user_id="user-1", email="u1@example.com", display_name="User 1", password_hash="x", created_at=now, updated_at=now),
                    UserRecord(user_id="user-2", email="u2@example.com", display_name="User 2", password_hash="x", created_at=now, updated_at=now),
                ])
                session.commit()

            service = ProjectService(Path(temp_dir), header_store=SqlHeaderStore(session_factory))
            owned = service.create_project(CreateProjectRequest(name="Owned"), "user-1")
            service.create_project(CreateProjectRequest(name="Other"), "user-2")

            self.assertEqual([project.project_id for project in service.list_projects_for_user("user-1")], [owned.project_id])
            self.assertEqual(service.get_project_for_user(owned.project_id, "user-1").project_id, owned.project_id)
            with self.assertRaises(FileNotFoundError):
                service.get_project_for_user(owned.project_id, "user-2")


if __name__ == "__main__":
    unittest.main()
