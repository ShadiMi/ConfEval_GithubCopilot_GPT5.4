ALLOWED_BUILDINGS = {
    "ENG": "Engineering Building",
    "SCI": "Science Hall",
    "LIB": "Library Annex",
    "BUS": "Business Center",
}


class LocationValidationError(ValueError):
    pass


def build_location_label(
    *,
    building: str | None,
    floor: int | None,
    room: int | None,
    location_text: str | None,
) -> str:
    if location_text:
        return location_text.strip()

    if not building or floor is None or room is None:
        raise LocationValidationError("Either free-text location or complete structured location is required")

    if building not in ALLOWED_BUILDINGS:
        raise LocationValidationError("Building is not allowed")
    if floor not in {1, 2}:
        raise LocationValidationError("Floor must be 1 or 2")

    valid_rooms = range(101, 110) if floor == 1 else range(201, 210)
    if room not in valid_rooms:
        raise LocationValidationError("Room is invalid for the selected floor")

    return f"{ALLOWED_BUILDINGS[building]}, Floor {floor}, Room {room}"
