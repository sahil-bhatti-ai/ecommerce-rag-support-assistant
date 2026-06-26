from app.services.confidence import compute_confidence, is_grounded


def test_confidence_empty_scores() -> None:
    assert compute_confidence([]) == 0.0


def test_confidence_is_bounded() -> None:
    assert compute_confidence([1.2, 0.9]) == 1.0


def test_grounding_threshold() -> None:
    assert is_grounded(0.8, 0.45) is True
    assert is_grounded(0.2, 0.45) is False
