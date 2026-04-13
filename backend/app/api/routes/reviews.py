from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.models.enums import UserRole
from app.models.review import Review
from app.models.user import User
from app.schemas.review import (
    AdminProjectAssignmentListResponse,
    AdminProjectAssignmentResponse,
    ProjectCompletedReviewsResponse,
    ProjectReviewerAssignmentRequest,
    ReviewCriterionScoreResponse,
    ReviewerAssignedProjectListResponse,
    ReviewerAssignedProjectResponse,
    ReviewResponse,
    ReviewUpsertRequest,
    ReviewWorkspaceResponse,
)
from app.schemas.user import UserSummary
from app.services.review_service import ReviewService

router = APIRouter()


def _serialize_review(review: Review) -> ReviewResponse:
    criterion_scores = sorted(review.criterion_scores, key=lambda item: item.criteria.display_order)
    return ReviewResponse(
        id=review.id,
        project_id=review.project_id,
        reviewer_id=review.reviewer_id,
        session_id=review.session_id,
        status=review.status,
        overall_comment=review.overall_comment,
        total_score=float(review.total_score) if review.total_score is not None else None,
        created_at=review.created_at,
        updated_at=review.updated_at,
        reviewer=UserSummary.model_validate(review.reviewer),
        criterion_scores=[
            ReviewCriterionScoreResponse(
                criteria_id=item.criteria_id,
                criteria_name=item.criteria.name,
                description=item.criteria.description,
                max_score=item.criteria.max_score,
                weight=float(item.criteria.weight),
                display_order=item.criteria.display_order,
                score=float(item.score),
            )
            for item in criterion_scores
        ],
    )


@router.get("/admin/assignments", response_model=AdminProjectAssignmentListResponse)
def list_assignment_projects(
    db: DbSession,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> AdminProjectAssignmentListResponse:
    service = ReviewService(db)
    projects = service.list_projects_for_assignment()
    return AdminProjectAssignmentListResponse(
        projects=[
            AdminProjectAssignmentResponse(
                id=project.id,
                title=project.title,
                description=project.description,
                status=project.status,
                poster_number=project.poster_number,
                session_id=project.session.id,
                session_name=project.session.name,
                reviewers_per_project=project.session.reviewers_per_project,
                owner=UserSummary.model_validate(project.owner),
                assigned_reviewers=[UserSummary.model_validate(user) for user in project.assigned_reviewers],
                eligible_reviewers=[UserSummary.model_validate(user) for user in project.session.reviewers if user.is_active and user.is_approved and user.is_reviewer],
                submitted_review_count=sum(1 for review in project.reviews if review.status.value == "submitted"),
                average_score=(
                    round(
                        sum(float(review.total_score) for review in project.reviews if review.status.value == "submitted" and review.total_score is not None)
                        / sum(1 for review in project.reviews if review.status.value == "submitted" and review.total_score is not None),
                        2,
                    )
                    if any(review.status.value == "submitted" and review.total_score is not None for review in project.reviews)
                    else None
                ),
            )
            for project in projects
        ]
    )


@router.put("/projects/{project_id}/assignments", response_model=AdminProjectAssignmentResponse)
def assign_project_reviewers(
    project_id: str,
    payload: ProjectReviewerAssignmentRequest,
    db: DbSession,
    current_admin: User = Depends(require_roles(UserRole.ADMIN)),
) -> AdminProjectAssignmentResponse:
    service = ReviewService(db)
    try:
        project = service.assign_reviewers(actor=current_admin, project_id=project_id, reviewer_ids=payload.reviewer_ids)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AdminProjectAssignmentResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        status=project.status,
        poster_number=project.poster_number,
        session_id=project.session.id,
        session_name=project.session.name,
        reviewers_per_project=project.session.reviewers_per_project,
        owner=UserSummary.model_validate(project.owner),
        assigned_reviewers=[UserSummary.model_validate(user) for user in project.assigned_reviewers],
        eligible_reviewers=[UserSummary.model_validate(user) for user in project.session.reviewers if user.is_active and user.is_approved and user.is_reviewer],
        submitted_review_count=sum(1 for review in project.reviews if review.status.value == "submitted"),
        average_score=(
            round(
                sum(float(review.total_score) for review in project.reviews if review.status.value == "submitted" and review.total_score is not None)
                / sum(1 for review in project.reviews if review.status.value == "submitted" and review.total_score is not None),
                2,
            )
            if any(review.status.value == "submitted" and review.total_score is not None for review in project.reviews)
            else None
        ),
    )


@router.get("/me/assignments", response_model=ReviewerAssignedProjectListResponse)
def list_my_review_assignments(
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewerAssignedProjectListResponse:
    service = ReviewService(db)
    try:
        projects = service.list_assigned_projects_for_reviewer(current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    serialized_projects: list[ReviewerAssignedProjectResponse] = []
    for project in projects:
        review = next((item for item in project.reviews if item.reviewer_id == current_user.id), None)
        if current_user.role == UserRole.ADMIN and review is None:
            review = next((item for item in project.reviews if item.status.value == "submitted"), None)
        serialized_projects.append(
            ReviewerAssignedProjectResponse(
                id=project.id,
                title=project.title,
                description=project.description,
                status=project.status,
                poster_number=project.poster_number,
                session_id=project.session.id,
                session_name=project.session.name,
                owner=UserSummary.model_validate(project.owner),
                assigned_reviewers=[UserSummary.model_validate(user) for user in project.assigned_reviewers],
                review_status=review.status if review is not None else None,
                total_score=float(review.total_score) if review is not None and review.total_score is not None else None,
                review_updated_at=review.updated_at if review is not None else None,
            )
        )
    return ReviewerAssignedProjectListResponse(projects=serialized_projects)


@router.get("/projects/{project_id}/me", response_model=ReviewWorkspaceResponse)
def get_my_review_workspace(project_id: str, db: DbSession, current_user: CurrentUser) -> ReviewWorkspaceResponse:
    service = ReviewService(db)
    try:
        project, review = service.get_reviewer_workspace(reviewer=current_user, project_id=project_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ReviewWorkspaceResponse(
        project_id=project.id,
        project_title=project.title,
        project_description=project.description,
        poster_number=project.poster_number,
        session_id=project.session.id,
        session_name=project.session.name,
        owner=UserSummary.model_validate(project.owner),
        assigned_reviewers=[UserSummary.model_validate(user) for user in project.assigned_reviewers],
        criteria=[criteria for criteria in sorted(project.session.criteria, key=lambda item: item.display_order)],
        review=_serialize_review(review) if review is not None else None,
    )


@router.put("/projects/{project_id}/me", response_model=ReviewResponse)
def save_my_review(
    project_id: str,
    payload: ReviewUpsertRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> ReviewResponse:
    service = ReviewService(db)
    try:
        review = service.upsert_review(
            reviewer=current_user,
            project_id=project_id,
            overall_comment=payload.overall_comment,
            criterion_scores=[(item.criteria_id, item.score) for item in payload.criterion_scores],
            submit=payload.submit,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _serialize_review(review)


@router.get("/projects/{project_id}/completed", response_model=ProjectCompletedReviewsResponse)
def get_project_completed_reviews(project_id: str, db: DbSession, current_user: CurrentUser) -> ProjectCompletedReviewsResponse:
    service = ReviewService(db)
    try:
        project, reviews, average_score = service.list_project_completed_reviews(actor=current_user, project_id=project_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ProjectCompletedReviewsResponse(
        project_id=project.id,
        project_title=project.title,
        submitted_review_count=len(reviews),
        average_score=average_score,
        reviews=[_serialize_review(review) for review in reviews],
    )