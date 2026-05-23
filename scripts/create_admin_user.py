from __future__ import annotations

import argparse
from pathlib import Path

from app.services.auth_service import AuthService
from app.storage.db import build_engine, build_session_factory
from app.storage.db_models import Base


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    engine = build_engine(base_dir)
    Base.metadata.create_all(engine)
    session_factory = build_session_factory(engine)

    auth_service = AuthService(session_factory=session_factory)
    email, user_id = auth_service.create_or_update_user(
        email=args.email,
        display_name=args.display_name,
        password=args.password,
    )
    print(f"ok:{email}:{user_id}")


if __name__ == "__main__":
    main()
