import pytest

from app.utils.calculations import ReviewCalculationError, calculate_project_average, calculate_weighted_total
from app.utils.location import LocationValidationError, build_location_label


def test_build_location_label_from_structured_fields() -> None:
    label = build_location_label(building="ENG", floor=1, room=103, location_text=None)
    assert label == "Engineering Building, Floor 1, Room 103"


def test_build_location_label_rejects_invalid_room() -> None:
    with pytest.raises(LocationValidationError):
        build_location_label(building="ENG", floor=1, room=202, location_text=None)


def test_calculate_weighted_total_returns_two_decimal_places() -> None:
    total = calculate_weighted_total([(80, 100, 1.5), (90, 100, 2.0), (70, 100, 1.0)])
    assert total == 81.11


def test_calculate_weighted_total_rejects_invalid_scores() -> None:
    with pytest.raises(ReviewCalculationError):
        calculate_weighted_total([(120, 100, 1.0)])


def test_calculate_project_average() -> None:
    assert calculate_project_average([81.11, 77.89, 92.0]) == 83.67
