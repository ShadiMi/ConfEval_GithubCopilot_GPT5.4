from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.dependencies import CurrentUser, DbSession
from app.schemas.auth import TokenRefreshRequest
from app.schemas.common import TokenPair
from app.schemas.user import CurrentUserResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest, db: DbSession) -> UserResponse:
    service = AuthService(db)
    try:
        user = service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@router.post("/register/external-reviewer", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_external_reviewer(
    db: DbSession,
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    full_name: Annotated[str, Form()],
    affiliation: Annotated[str, Form()],
    phone_number: Annotated[str | None, Form()] = None,
    id_number: Annotated[str | None, Form()] = None,
    cv_file: UploadFile = File(...),
) -> UserResponse:
    payload = UserRegisterRequest(
        email=email,
        password=password,
        full_name=full_name,
        role="external_reviewer",
        affiliation=affiliation,
        phone_number=phone_number,
        id_number=id_number,
    )
    service = AuthService(db)
    try:
        user = await service.register_external_reviewer(payload, cv_file)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenPair)
def login(payload: UserLoginRequest, db: DbSession) -> TokenPair:
    service = AuthService(db)
    try:
        return service.login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: TokenRefreshRequest, db: DbSession) -> TokenPair:
    service = AuthService(db)
    try:
        return service.refresh_tokens(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: CurrentUser) -> CurrentUserResponse:
    return CurrentUserResponse(user=UserResponse.model_validate(current_user))
