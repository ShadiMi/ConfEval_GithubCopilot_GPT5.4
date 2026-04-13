from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.seed import seed_reference_data


def bootstrap_reference_data() -> dict[str, list[str]]:
    with SessionLocal() as db:
        return seed_reference_data(db)


if __name__ == "__main__":
    result = bootstrap_reference_data()
    print(result)
