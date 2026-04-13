from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import DbSession, require_roles
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.tag import TagCreateRequest, TagListResponse, TagResponse
from app.services.tag_service import TagService

router = APIRouter()


@router.get("", response_model=TagListResponse)
def list_tags(db: DbSession) -> TagListResponse:
    service = TagService(db)
    tags = service.list_tags()
    return TagListResponse(tags=[TagResponse.model_validate(tag) for tag in tags])


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    payload: TagCreateRequest,
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> TagResponse:
    service = TagService(db)
    try:
        tag = service.create_tag(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TagResponse.model_validate(tag)
