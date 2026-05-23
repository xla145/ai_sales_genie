from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

import bcrypt
import jwt
from sqlalchemy.orm import Session, sessionmaker

from app.storage.db import session_scope
from app.storage.db_models import UserRecord


class AuthError(Exception):
    pass


class AuthConflictError(AuthError):
    pass


@dataclass
class AuthSession:
    user_id: str
    email: str
    expires_at: float


@dataclass
class AuthUserSnapshot:
    user_id: str
    email: str
    display_name: str
    password_hash: str
    status: str


@dataclass
class AuthService:
    session_factory: sessionmaker[Session]
    jwt_secret: str = field(default_factory=lambda: os.environ.get("AUTH_JWT_SECRET", "dev-secret-change-me"))
    jwt_alg: str = field(default_factory=lambda: os.environ.get("AUTH_JWT_ALG", "HS256"))
    token_ttl_seconds: int = field(default_factory=lambda: int(os.environ.get("AUTH_TOKEN_TTL", "86400")))

    def login(self, email: str, password: str) -> tuple[str, str]:
        normalized_email = email.strip().lower()
        user = self._get_user(normalized_email)
        if user is None or user.status != "active":
            raise AuthError("邮箱或密码错误")
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            raise AuthError("邮箱或密码错误")

        token = self._issue_token(user.email)
        return token, user.email

    def register(self, email: str, password: str, display_name: str | None = None) -> tuple[str, str]:
        normalized_email = email.strip().lower()
        if self._get_user(normalized_email) is not None:
            raise AuthConflictError("邮箱已被注册")

        user_display_name = (display_name or "").strip() or normalized_email.split("@")[0]
        self.create_or_update_user(normalized_email, user_display_name, password)
        token = self._issue_token(normalized_email)
        return token, normalized_email

    def logout(self, token: str | None) -> None:
        return None

    def get_user(self, token: str | None) -> AuthSession | None:
        if not token:
            return None

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_alg])
        except jwt.PyJWTError:
            return None

        subject = str(payload.get("sub") or "").strip().lower()
        exp = float(payload.get("exp") or 0)
        if not subject or exp <= time.time():
            return None

        user = self._get_user(subject)
        if user is None or user.status != "active":
            return None

        return AuthSession(user_id=user.user_id, email=user.email, expires_at=exp)

    def display_name(self, email: str) -> str:
        user = self._get_user(email.strip().lower())
        if user is not None and user.display_name:
            return user.display_name
        return email.split("@")[0] if email else ""

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def create_or_update_user(self, email: str, display_name: str, password: str) -> tuple[str, str]:
        normalized_email = email.strip().lower()
        now = datetime.now()
        with session_scope(self.session_factory) as session:
            user = session.query(UserRecord).filter(UserRecord.email == normalized_email).first()
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            if user is None:
                user = UserRecord(
                    user_id=f"user_{uuid4().hex[:8]}",
                    email=normalized_email,
                    display_name=display_name.strip() or normalized_email.split("@")[0],
                    password_hash=password_hash,
                    status="active",
                    created_at=now,
                    updated_at=now,
                )
                session.add(user)
            else:
                user.display_name = display_name.strip() or user.display_name
                user.password_hash = password_hash
                user.status = "active"
                user.updated_at = now
                session.add(user)
            session.flush()
            return user.email, user.user_id

    def _issue_token(self, email: str) -> str:
        now = int(time.time())
        payload = {
            "sub": email,
            "iat": now,
            "exp": now + self.token_ttl_seconds,
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_alg)

    def _get_user(self, email: str) -> AuthUserSnapshot | None:
        with session_scope(self.session_factory) as session:
            user = session.query(UserRecord).filter(UserRecord.email == email).first()
            if user is None:
                return None
            return AuthUserSnapshot(
                user_id=user.user_id,
                email=user.email,
                display_name=user.display_name or "",
                password_hash=user.password_hash,
                status=user.status,
            )
