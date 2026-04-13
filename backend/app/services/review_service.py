from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conference import Criteria, Session as ConferenceSession
from app.models.enums import AuditEventType, NotificationType, ProjectStatus, ReviewStatus, UserRole
from app.models.notification import AuditLog
from app.models.project import Project
from app.models.review import Review, ReviewCriterionScore
from app.models.user import User
from app.services.notification_service import NotificationService
from app.utils.calculations import ReviewCalculationError, calculate_project_average, calculate_weighted_total


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def _project_query(self):
        return select(Project).options(
            selectinload(Project.owner),
            selectinload(Project.team_members),
            selectinload(Project.assigned_reviewers),
            selectinload(Project.session).selectinload(ConferenceSession.criteria),
            selectinload(Project.session).selectinload(ConferenceSession.reviewers),
            selectinload(Project.reviews).selectinload(Review.reviewer),
            selectinload(Project.reviews).selectinload(Review.criterion_scores).selectinload(ReviewCriterionScore.criteria),
        )

    def get_project(self, project_id: UUID | str) -> Project:
        project = self.db.scalar(self._project_query().where(Project.id == UUID(str(project_id))))
        if project is None:
            raise ValueError("Project not found")
        return project

    def list_projects_for_assignment(self) -> list[Project]:
        return list(
            self.db.scalars(
                self._project_query()
                .where(Project.status == ProjectStatus.APPROVED)
                .where(Project.session_id.is_not(None))
                .order_by(Project.created_at.asc())
            )
        )

    def list_assigned_projects_for_reviewer(self, reviewer: User) -> list[Project]:
        if reviewer.role not in {UserRole.INTERNAL_REVIEWER, UserRole.EXTERNAL_REVIEWER, UserRole.ADMIN}:
            raise PermissionError("Only reviewers can access assigned projects")

        if reviewer.role == UserRole.ADMIN:
            return self.list_projects_for_assignment()

        return list(
            self.db.scalars(
                self._project_query()
                .where(Project.assigned_reviewers.any(User.id == reviewer.id))
                .order_by(Project.created_at.asc())
            )
        )

    def assign_reviewers(self, *, actor: User, project_id: UUID | str, reviewer_ids: list[UUID]) -> Project:
        if actor.role != UserRole.ADMIN:
            raise PermissionError("Only admins can assign reviewers")

        project = self.get_project(project_id)
        if project.status != ProjectStatus.APPROVED:
            raise ValueError("Only approved projects can receive reviewer assignments")
        if project.session is None:
            raise ValueError("Project must belong to a session before assigning reviewers")

        unique_reviewer_ids = list(dict.fromkeys(reviewer_ids))
        if len(unique_reviewer_ids) > project.session.reviewers_per_project:
            raise ValueError("Reviewer selection exceeds the session reviewer limit")

        eligible_reviewers = {
            reviewer.id: reviewer
            for reviewer in project.session.reviewers
            if reviewer.is_active and reviewer.is_approved and reviewer.is_reviewer
        }
        invalid_ids = [reviewer_id for reviewer_id in unique_reviewer_ids if reviewer_id not in eligible_reviewers]
        if invalid_ids:
            raise ValueError("One or more selected reviewers are not eligible for this session")

        existing_reviewer_ids = {reviewer.id for reviewer in project.assigned_reviewers}
        removed_reviewer_ids = existing_reviewer_ids.difference(unique_reviewer_ids)
        if any(review.reviewer_id in removed_reviewer_ids for review in project.reviews):
            raise ValueError("Cannot remove a reviewer after a review has been started")

        project.assigned_reviewers = [eligible_reviewers[reviewer_id] for reviewer_id in unique_reviewer_ids]

        for reviewer_id in set(unique_reviewer_ids).difference(existing_reviewer_ids):
            reviewer = eligible_reviewers[reviewer_id]
            self.notifications.create_notification(
                user=reviewer,
                notification_type=NotificationType.REVIEWER_ASSIGNED,
                title="Project assigned",
                message=f"You have been assigned to review '{project.title}'.",
                link="/dashboard/reviewer/assignments",
            )

        self.db.add(
            AuditLog(
                actor=actor,
                event_type=AuditEventType.REVIEWER_ASSIGNED,
                resource_type="project",
                resource_id=str(project.id),
                metadata_json={"reviewer_ids": [str(reviewer_id) for reviewer_id in unique_reviewer_ids]},
            )
        )
        self.db.commit()
        self.db.refresh(project)
        return self.get_project(project.id)

    def get_reviewer_workspace(self, *, reviewer: User, project_id: UUID | str) -> tuple[Project, Review | None]:
        project = self.get_project(project_id)
        if project.session is None:
            raise ValueError("Project session not found")

        if reviewer.role != UserRole.ADMIN and all(assigned.id != reviewer.id for assigned in project.assigned_reviewers):
            raise PermissionError("Reviewer is not assigned to this project")

        review = next((item for item in project.reviews if item.reviewer_id == reviewer.id), None)
        return project, review

    def upsert_review(
        self,
        *,
        reviewer: User,
        project_id: UUID | str,
        overall_comment: str | None,
        criterion_scores: list[tuple[UUID, float]],
        submit: bool,
    ) -> Review:
        if reviewer.role not in {UserRole.INTERNAL_REVIEWER, UserRole.EXTERNAL_REVIEWER}:
            raise PermissionError("Only reviewers can create or submit reviews")

        project, review = self.get_reviewer_workspace(reviewer=reviewer, project_id=project_id)
        if project.status != ProjectStatus.APPROVED:
            raise ValueError("Only approved projects can be reviewed")
        if review is not None and review.status == ReviewStatus.SUBMITTED:
            raise ValueError("Submitted reviews cannot be edited")
        if project.session is None:
            raise ValueError("Project session not found")

        criteria_by_id = {criteria.id: criteria for criteria in project.session.criteria}
        if not criteria_by_id:
            raise ValueError("Session criteria are not configured")

        normalized_scores: dict[UUID, float] = {}
        for criteria_id, score in criterion_scores:
            if criteria_id in normalized_scores:
                raise ValueError("Each criterion can only be scored once")
            criteria = criteria_by_id.get(criteria_id)
            if criteria is None:
                raise ValueError("Review payload contains a criterion outside the assigned session")
            if score < 0 or score > criteria.max_score:
                raise ValueError(f"Score for '{criteria.name}' must be between 0 and {criteria.max_score}")
            normalized_scores[criteria_id] = score

        if review is None:
            review = Review(
                project=project,
                reviewer=reviewer,
                session_id=project.session.id,
                status=ReviewStatus.DRAFT,
            )
            self.db.add(review)
            self.db.flush()

        review.overall_comment = overall_comment.strip() if overall_comment else None
        review.criterion_scores = [
            ReviewCriterionScore(review=review, criteria=criteria_by_id[criteria_id], score=score)
            for criteria_id, score in normalized_scores.items()
        ]

        complete_score_count = len(normalized_scores) == len(criteria_by_id)
        if complete_score_count:
            try:
                review.total_score = calculate_weighted_total(
                    (
                        score,
                        criteria_by_id[criteria_id].max_score,
                        float(criteria_by_id[criteria_id].weight),
                    )
                    for criteria_id, score in normalized_scores.items()
                )
            except ReviewCalculationError as exc:
                raise ValueError(str(exc)) from exc
        else:
            review.total_score = None

        if submit:
            missing_criteria = [criteria.name for criteria_id, criteria in criteria_by_id.items() if criteria_id not in normalized_scores]
            if missing_criteria:
                raise ValueError("All session criteria must be scored before submission")
            review.status = ReviewStatus.SUBMITTED
            self.db.add(
                AuditLog(
                    actor=reviewer,
                    event_type=AuditEventType.REVIEW_SUBMITTED,
                    resource_type="review",
                    resource_id=str(review.id),
                    metadata_json={"project_id": str(project.id), "session_id": str(project.session.id)},
                )
            )
            self.notifications.create_notification(
                user=project.owner,
                notification_type=NotificationType.REVIEW_COMPLETED,
                title="Project review submitted",
                message=f"A completed review is now available for '{project.title}'.",
                link=f"/dashboard/student/projects/{project.id}/reviews",
            )
            for team_member in project.team_members:
                if team_member.id != project.owner_id:
                    self.notifications.create_notification(
                        user=team_member,
                        notification_type=NotificationType.REVIEW_COMPLETED,
                        title="Project review submitted",
                        message=f"A completed review is now available for '{project.title}'.",
                        link=f"/dashboard/student/projects/{project.id}/reviews",
                    )
        else:
            review.status = ReviewStatus.DRAFT

        self.db.commit()
        self.db.refresh(review)
        return self.get_review(review.id)

    def get_review(self, review_id: UUID | str) -> Review:
        review = self.db.scalar(
            select(Review)
            .where(Review.id == UUID(str(review_id)))
            .options(
                selectinload(Review.reviewer),
                selectinload(Review.criterion_scores).selectinload(ReviewCriterionScore.criteria),
            )
        )
        if review is None:
            raise ValueError("Review not found")
        return review

    def list_project_completed_reviews(self, *, actor: User, project_id: UUID | str) -> tuple[Project, list[Review], float | None]:
        project = self.get_project(project_id)
        is_project_member = actor.id == project.owner_id or any(member.id == actor.id for member in project.team_members)
        if actor.role != UserRole.ADMIN and not is_project_member:
            raise PermissionError("Only project members can view completed reviews")

        completed_reviews = [review for review in project.reviews if review.status == ReviewStatus.SUBMITTED]
        average_score = calculate_project_average(review.total_score for review in completed_reviews if review.total_score is not None) if completed_reviews else None
        return project, completed_reviews, average_score