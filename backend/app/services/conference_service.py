from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conference import Conference, Criteria, Session as ConferenceSession
from app.models.enums import ConferenceStatus, SessionStatus, UserRole
from app.models.tag import Tag
from app.schemas.conference import ConferenceCreateRequest, SessionCreateRequest
from app.utils.location import build_location_label


class ConferenceService:
    def __init__(self, db: Session):
        self.db = db

    def list_conferences(self, role: UserRole) -> list[Conference]:
        query = select(Conference).options(
            selectinload(Conference.sessions).selectinload(ConferenceSession.tags),
            selectinload(Conference.sessions).selectinload(ConferenceSession.criteria),
        )
        if role != UserRole.ADMIN:
            query = query.where(Conference.status == ConferenceStatus.ACTIVE)
        return list(self.db.scalars(query.order_by(Conference.start_date.desc())))

    def create_conference(self, payload: ConferenceCreateRequest) -> Conference:
        location_label = build_location_label(
            building=payload.building,
            floor=payload.floor,
            room=payload.room,
            location_text=payload.location_text,
        )
        conference = Conference(
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status,
            location_label=location_label,
            location_text=payload.location_text.strip() if payload.location_text else None,
            location_building=payload.building,
            location_floor=payload.floor,
            location_room=payload.room,
        )
        self.db.add(conference)
        self.db.commit()
        self.db.refresh(conference)
        return self.get_conference(conference.id)

    def get_conference(self, conference_id) -> Conference:
        conference = self.db.scalar(
            select(Conference)
            .where(Conference.id == conference_id)
            .options(
                selectinload(Conference.sessions).selectinload(ConferenceSession.tags),
                selectinload(Conference.sessions).selectinload(ConferenceSession.criteria),
            )
        )
        if conference is None:
            raise ValueError("Conference not found")
        return conference

    def list_sessions(self, role: UserRole) -> list[ConferenceSession]:
        query = select(ConferenceSession).options(
            selectinload(ConferenceSession.tags),
            selectinload(ConferenceSession.criteria),
        )
        if role != UserRole.ADMIN:
            query = query.where(ConferenceSession.status.in_([SessionStatus.UPCOMING, SessionStatus.ACTIVE]))
        return list(self.db.scalars(query.order_by(ConferenceSession.start_date.desc())))

    def create_session(self, payload: SessionCreateRequest) -> ConferenceSession:
        tags = []
        if payload.tag_ids:
            tags = list(self.db.scalars(select(Tag).where(Tag.id.in_(payload.tag_ids))))
            if len(tags) != len(payload.tag_ids):
                raise ValueError("One or more tags were not found")

        session = ConferenceSession(
            conference_id=payload.conference_id,
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status,
            location_label=payload.location_text.strip(),
            location_text=payload.location_text.strip(),
            max_project_capacity=payload.max_project_capacity,
            reviewers_per_project=payload.reviewers_per_project,
            tags=tags,
        )
        for criterion_payload in payload.criteria:
            session.criteria.append(
                Criteria(
                    name=criterion_payload.name.strip(),
                    description=criterion_payload.description.strip() if criterion_payload.description else None,
                    max_score=criterion_payload.max_score,
                    weight=criterion_payload.weight,
                    display_order=criterion_payload.display_order,
                )
            )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self.get_session(session.id)

    def get_session(self, session_id) -> ConferenceSession:
        session = self.db.scalar(
            select(ConferenceSession)
            .where(ConferenceSession.id == session_id)
            .options(selectinload(ConferenceSession.tags), selectinload(ConferenceSession.criteria))
        )
        if session is None:
            raise ValueError("Session not found")
        return session
