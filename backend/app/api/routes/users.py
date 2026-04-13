from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.core.dependencies import DbSession, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import PendingReviewerListResponse, ReviewerApprovalDecisionRequest
from app.schemas.user import UserResponse
from app.services.file_service import FileStorageService
from app.services.user_service import UserService

router = APIRouter()


@router.get("/pending-reviewers", response_model=PendingReviewerListResponse)
def list_pending_reviewers(
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> PendingReviewerListResponse:
    service = UserService(db)
    users = service.list_pending_reviewers()
    return PendingReviewerListResponse(users=service.summarize_pending_reviewers(users))


@router.patch("/{user_id}/reviewer-approval", response_model=UserResponse)
def decide_reviewer_approval(
    user_id: str,
    payload: ReviewerApprovalDecisionRequest,
    db: DbSession,
    current_admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> UserResponse:
    service = UserService(db)
    try:
        user = service.decide_reviewer(
            actor=current_admin,
            user_id=user_id,
            approved=payload.approved,
            reason=payload.reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserResponse.model_validate(user)


@router.get("/{user_id}/cv")
def download_reviewer_cv(
    user_id: str,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> FileResponse:
    service = FileStorageService(db)
    asset = service.get_reviewer_cv_asset(user_id)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer CV not found")

    file_path = service.resolve_storage_path(asset)
    if not Path(file_path).exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reviewer CV file is missing")

    return FileResponse(path=file_path, media_type=asset.content_type, filename=asset.file_name)
