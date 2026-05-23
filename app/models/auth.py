from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)
    display_name: str | None = None


class LoginResponse(BaseModel):
    token: str
    email: str
    display_name: str


class UserInfo(BaseModel):
    email: str
    display_name: str
