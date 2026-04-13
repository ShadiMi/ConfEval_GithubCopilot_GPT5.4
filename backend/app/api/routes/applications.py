from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.application import (
    ReviewerApplicationCreateRequest,
    ReviewerApplicationDecisionRequest,
    ReviewerApplicationListResponse,
    ReviewerApplicationResponse,
)
from app.services.application_service import ReviewerApplicationService

router = APIRouter()


@router.get("/me", response_model=ReviewerApplicationListResponse)
def list_my_applications(db: DbSession, current_user: CurrentUser) -> ReviewerApplicationListResponse:
    service = ReviewerApplicationService(db)
    applications = service.list_reviewer_applications(current_user)
    return ReviewerApplicationListResponse(
        applications=[ReviewerApplicationResponse.model_validate(item) for item in applications]
    )


@router.post("", response_model=ReviewerApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_session(
    payload: ReviewerApplicationCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewerApplicationResponse:
    service = ReviewerApplicationService(db)
    try:
        application = service.apply_to_session(
            reviewer=current_user,
            session_id=payload.session_id,
            cover_message=payload.cover_message,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ReviewerApplicationResponse.model_validate(application)


@router.get("/pending", response_model=ReviewerApplicationListResponse)
def list_pending_applications(
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> ReviewerApplicationListResponse:
    service = ReviewerApplicationService(db)
    applications = service.list_pending_applications()
    return ReviewerApplicationListResponse(
        applications=[ReviewerApplicationResponse.model_validate(item) for item in applications]
    )


@router.patch("/{application_id}/decision", response_model=ReviewerApplicationResponse)
def decide_application(
    application_id: str,
    payload: ReviewerApplicationDecisionRequest,
    db: DbSession,
    current_admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> ReviewerApplicationResponse:
    service = ReviewerApplicationService(db)
    try:
        application = service.decide_application(
            actor=current_admin,
            application_id=application_id,
            approved=payload.approved,
            decision_notes=payload.decision_notes,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ReviewerApplicationResponse.model_validate(application)
