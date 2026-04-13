from unittest.mock import Mock

from app.db.seed import DEFAULT_ADMIN_EMAIL, seed_default_admin, seed_reference_data


def test_seed_default_admin_creates_admin_when_missing() -> None:
    db = Mock()
    db.scalar.return_value = None

    seed_default_admin(db)

    db.add.assert_called_once()
    admin_user = db.add.call_args.args[0]
    assert admin_user.email == DEFAULT_ADMIN_EMAIL


def test_seed_reference_data_commits() -> None:
    db = Mock()
    db.scalar.return_value = None

    result = seed_reference_data(db)

    assert DEFAULT_ADMIN_EMAIL in result["seeded_admin"]
    assert "ENG" in result["allowed_buildings"]
    db.commit.assert_called_once()
