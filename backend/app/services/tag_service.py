from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tag import Tag
from app.schemas.tag import TagCreateRequest


class TagService:
    def __init__(self, db: Session):
        self.db = db

    def list_tags(self) -> list[Tag]:
        return list(self.db.scalars(select(Tag).order_by(Tag.name.asc())))

    def create_tag(self, payload: TagCreateRequest) -> Tag:
        existing = self.db.scalar(select(Tag).where(Tag.name == payload.name.strip()))
        if existing is not None:
            raise ValueError("Tag name already exists")

        tag = Tag(name=payload.name.strip(), description=payload.description.strip() if payload.description else None)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag
