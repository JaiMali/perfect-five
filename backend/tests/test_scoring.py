import pytest

try:
    from backend.scoring import (
        generate_reference,
        normalize_points,
        calculate_score,
        get_bounding_box,
    )
except ImportError:
    from scoring import (
        generate_reference,
        normalize_points,
        calculate_score,
        get_bounding_box,
    )


def test_generate_reference_returns_points():
    points = generate_reference("5")
    assert len(points) > 0
    assert all(isinstance(p, tuple) and len(p) == 2 for p in points)


def test_generate_reference_different_characters():
    points_5 = generate_reference("5")
    points_8 = generate_reference("8")
    assert points_5 != points_8


def test_get_bounding_box_empty():
    assert get_bounding_box([]) == (0, 0, 0, 0)


def test_get_bounding_box_single_point():
    result = get_bounding_box([(50, 50)])
    assert result == (50, 50, 50, 50)


def test_get_bounding_box_multiple_points():
    points = [(10, 20), (30, 40), (50, 60)]
    result = get_bounding_box(points)
    assert result == (10, 20, 50, 60)


def test_normalize_points_empty():
    assert normalize_points([]) == []


def test_normalize_points_single():
    points = [(50, 50)]
    assert normalize_points(points) == points


def test_normalize_points_scales():
    points = [(0, 0), (100, 100)]
    normalized = normalize_points(points)
    assert all(0 <= p[0] <= 100 and 0 <= p[1] <= 100 for p in normalized)


def test_calculate_score_few_points():
    ref = generate_reference("5")
    score = calculate_score([(0, 0)], ref)
    assert score == 0.0


def test_calculate_score_valid_range():
    ref = generate_reference("5")
    user = [(i * 5, i * 5) for i in range(100)]
    score = calculate_score(user, ref)
    assert 0 <= score <= 100


def test_calculate_score_perfect_match():
    ref = generate_reference("5")
    score = calculate_score(ref, ref)
    assert score >= 90
