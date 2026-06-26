from statistics import mean


def compute_confidence(scores: list[float]) -> float:
    """Map vector scores to a conservative confidence value in [0, 1]."""
    if not scores:
        return 0.0
    top_score = max(scores)
    avg_top_3 = mean(sorted(scores, reverse=True)[:3])
    confidence = (0.7 * top_score) + (0.3 * avg_top_3)
    return round(max(0.0, min(1.0, confidence)), 3)


def is_grounded(confidence: float, threshold: float) -> bool:
    return confidence >= threshold
