from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.enums import UserRole
from app.models.user import User
from app.utils.location import ALLOWED_BUILDINGS


DEFAULT_ADMIN_EMAIL = "admin@confeval.com"
DEFAULT_ADMIN_PASSWORD = "Admin123!"


def seed_default_admin(db: Session) -> None:
    existing_admin = db.scalar(select(User).where(User.email == DEFAULT_ADMIN_EMAIL))
    if existing_admin is not None:
        return

    db.add(
        User(
            email=DEFAULT_ADMIN_EMAIL,
            password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
            full_name="Initial Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True,
            requires_manual_approval=False,
        )
    )


def seed_reference_data(db: Session) -> dict[str, list[str]]:
    seed_default_admin(db)
    db.commit()
    return {"allowed_buildings": list(ALLOWED_BUILDINGS.keys()), "seeded_admin": [DEFAULT_ADMIN_EMAIL]}
