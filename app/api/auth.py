from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import get_auth_service
from app.models.auth import LoginRequest, LoginResponse, RegisterRequest, UserInfo
from app.services.auth_service import AuthConflictError, AuthError, AuthService, AuthSession

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: AuthServiceDep,
) -> AuthSession:
    token = credentials.credentials if credentials is not None else None
    session = auth_service.get_user(token)
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已过期")
    return session


CurrentUserDep = Annotated[AuthSession, Depends(get_current_user)]


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, auth_service: AuthServiceDep) -> LoginResponse:
    try:
        token, email = auth_service.login(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return LoginResponse(
        token=token,
        email=email,
        display_name=auth_service.display_name(email),
    )


@router.post("/register", response_model=LoginResponse)
def register(payload: RegisterRequest, auth_service: AuthServiceDep) -> LoginResponse:
    try:
        token, email = auth_service.register(payload.email, payload.password, payload.display_name)
    except AuthConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return LoginResponse(
        token=token,
        email=email,
        display_name=auth_service.display_name(email),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth_service: AuthServiceDep,
) -> Response:
    token = credentials.credentials if credentials is not None else None
    auth_service.logout(token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserInfo)
def me(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> UserInfo:
    return UserInfo(
        email=current_user.email,
        display_name=auth_service.display_name(current_user.email),
    )
