from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.enums import FileAssetKind, UserRole
from app.models.user import User
from app.schemas.project import ProjectDecisionRequest, ProjectListResponse, ProjectSummary
from app.schemas.team import PendingInvitationListResponse, ProjectTeamResponse, TeamInvitationCreateRequest, TeamInvitationResponse
from app.services.file_service import FileStorageService, FileValidationError
from app.services.project_service import ProjectService
from app.services.team_service import TeamService

router = APIRouter()


@router.post("", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
async def create_project(
    db: DbSession,
    current_user: CurrentUser,
    title: Annotated[str, Form()],
    description: Annotated[str, Form()],
    mentor_email: Annotated[str | None, Form()] = None,
    session_id: Annotated[str | None, Form()] = None,
    paper_file: UploadFile | None = File(default=None),
    slides_file: UploadFile | None = File(default=None),
    additional_file: UploadFile | None = File(default=None),
) -> ProjectSummary:
    service = ProjectService(db)
    try:
        project = await service.create_project(
            owner=current_user,
            title=title,
            description=description,
            mentor_email=mentor_email,
            session_id=session_id,
            paper_upload=paper_file,
            slides_upload=slides_file,
            additional_upload=additional_file,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except (ValueError, FileValidationError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProjectSummary.model_validate(project)


@router.get("/me", response_model=ProjectListResponse)
def list_my_projects(db: DbSession, current_user: CurrentUser) -> ProjectListResponse:
    service = ProjectService(db)
    projects = service.list_owned_projects(current_user)
    return ProjectListResponse(projects=[ProjectSummary.model_validate(project) for project in projects])


@router.get("/pending", response_model=ProjectListResponse)
def list_pending_projects(
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> ProjectListResponse:
    service = ProjectService(db)
    projects = service.list_pending_projects()
    return ProjectListResponse(projects=[ProjectSummary.model_validate(project) for project in projects])


@router.patch("/{project_id}/decision", response_model=ProjectSummary)
def decide_project(
    project_id: str,
    payload: ProjectDecisionRequest,
    db: DbSession,
    current_admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> ProjectSummary:
    service = ProjectService(db)
    try:
        project = service.decide_project(
            actor=current_admin,
            project_id=project_id,
            approved=payload.approved,
            poster_number=payload.poster_number,
            reason=payload.reason,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ProjectSummary.model_validate(project)


@router.get("/{project_id}/attachments/{kind}")
def download_project_attachment(
    project_id: str,
    kind: FileAssetKind,
    db: DbSession,
    current_user: CurrentUser,
) -> FileResponse:
    if kind not in {
        FileAssetKind.PROJECT_PAPER,
        FileAssetKind.PROJECT_SLIDES,
        FileAssetKind.PROJECT_ADDITIONAL,
    }:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported attachment kind")

    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    if current_user.role != UserRole.ADMIN and project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    file_service = FileStorageService(db)
    asset = file_service.get_project_attachment(project_id, kind)
    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project attachment not found")
    file_path = file_service.resolve_storage_path(asset)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment file is missing")

    return FileResponse(path=file_path, media_type=asset.content_type, filename=asset.file_name)


@router.get("/{project_id}/team", response_model=ProjectTeamResponse)
def get_project_team(project_id: str, db: DbSession, current_user: CurrentUser) -> ProjectTeamResponse:
    service = TeamService(db)
    try:
        project = service.get_project_for_team(project_id)
        service.ensure_project_manager(current_user, project)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ProjectTeamResponse(
        project_id=project.id,
        owner=project.owner,
        team_members=project.team_members,
        pending_invitations=project.invitations,
    )


@router.post("/{project_id}/team-invitations", response_model=ProjectTeamResponse)
def invite_team_member(
    project_id: str,
    payload: TeamInvitationCreateRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectTeamResponse:
    service = TeamService(db)
    try:
        project = service.invite_team_member(actor=current_user, project_id=project_id, email=str(payload.email))
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ProjectTeamResponse(
        project_id=project.id,
        owner=project.owner,
        team_members=project.team_members,
        pending_invitations=project.invitations,
    )


@router.get("/team-invitations/me", response_model=PendingInvitationListResponse)
def list_my_pending_team_invitations(db: DbSession, current_user: CurrentUser) -> PendingInvitationListResponse:
    service = TeamService(db)
    invitations = service.list_pending_invitations_for_user(current_user)
    return PendingInvitationListResponse(invitations=[TeamInvitationResponse.model_validate(item) for item in invitations])


@router.post("/team-invitations/{token}/accept", response_model=TeamInvitationResponse)
def accept_team_invitation(token: str, db: DbSession, current_user: CurrentUser) -> TeamInvitationResponse:
    service = TeamService(db)
    try:
        invitation = service.respond_to_invitation(actor=current_user, token=token, accept=True)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TeamInvitationResponse.model_validate(invitation)


@router.post("/team-invitations/{token}/decline", response_model=TeamInvitationResponse)
def decline_team_invitation(token: str, db: DbSession, current_user: CurrentUser) -> TeamInvitationResponse:
    service = TeamService(db)
    try:
        invitation = service.respond_to_invitation(actor=current_user, token=token, accept=False)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TeamInvitationResponse.model_validate(invitation)
