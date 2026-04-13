from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.conference import (
    ConferenceCreateRequest,
    ConferenceListResponse,
    ConferenceResponse,
    SessionCreateRequest,
    SessionListResponse,
    SessionResponse,
)
from app.services.conference_service import ConferenceService
from app.utils.location import LocationValidationError

router = APIRouter()


@router.get("", response_model=ConferenceListResponse)
def list_conferences(db: DbSession, current_user: CurrentUser) -> ConferenceListResponse:
    service = ConferenceService(db)
    conferences = service.list_conferences(current_user.role)
    return ConferenceListResponse(conferences=[ConferenceResponse.model_validate(item) for item in conferences])


@router.post("", response_model=ConferenceResponse, status_code=status.HTTP_201_CREATED)
def create_conference(
    payload: ConferenceCreateRequest,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> ConferenceResponse:
    service = ConferenceService(db)
    try:
        conference = service.create_conference(payload)
    except (ValueError, LocationValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ConferenceResponse.model_validate(conference)


@router.get("/sessions", response_model=SessionListResponse)
def list_sessions(db: DbSession, current_user: CurrentUser) -> SessionListResponse:
    service = ConferenceService(db)
    sessions = service.list_sessions(current_user.role)
    return SessionListResponse(sessions=[SessionResponse.model_validate(item) for item in sessions])


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreateRequest,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> SessionResponse:
    service = ConferenceService(db)
    try:
        session = service.create_session(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SessionResponse.model_validate(session)
