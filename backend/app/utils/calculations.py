from collections.abc import Iterable
from decimal import Decimal, ROUND_HALF_UP


class ReviewCalculationError(ValueError):
    pass


def calculate_weighted_total(scores: Iterable[tuple[float, float, float]]) -> float:
    weighted_sum = Decimal("0")
    total_weight = Decimal("0")

    for score, max_score, weight in scores:
        score_decimal = Decimal(str(score))
        max_score_decimal = Decimal(str(max_score))
        weight_decimal = Decimal(str(weight))

        if max_score_decimal <= 0:
            raise ReviewCalculationError("Criterion max score must be positive")
        if weight_decimal <= 0:
            raise ReviewCalculationError("Criterion weight must be positive")
        if score_decimal < 0 or score_decimal > max_score_decimal:
            raise ReviewCalculationError("Criterion score must be within the configured max score")

        weighted_sum += score_decimal * weight_decimal
        total_weight += weight_decimal

    if total_weight == 0:
        raise ReviewCalculationError("At least one weighted criterion is required")

    return float((weighted_sum / total_weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_project_average(review_totals: Iterable[float]) -> float:
    totals = [Decimal(str(total)) for total in review_totals]
    if not totals:
        raise ReviewCalculationError("At least one completed review is required")
    return float((sum(totals) / Decimal(len(totals))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
