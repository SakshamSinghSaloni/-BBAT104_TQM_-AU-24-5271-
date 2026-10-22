"""
Unit tests for GradingService (FR-11: Auto-grading with case-insensitive short answers).
"""

import pytest
from backend.services.grading_service import GradingService


def test_short_answer_case_insensitivity():
    """Verify that short answers match regardless of casing."""
    correct = "Python"

    # Lowercase match
    is_correct, ratio, _ = GradingService.evaluate_answer("short_answer", "python", correct)
    assert is_correct is True
    assert ratio == 1

    # Uppercase match
    is_correct, ratio, _ = GradingService.evaluate_answer("short_answer", "PYTHON", correct)
    assert is_correct is True

    # Mixed case match
    is_correct, ratio, _ = GradingService.evaluate_answer("short_answer", "PyThOn", correct)
    assert is_correct is True


def test_short_answer_whitespace_trimming():
    """Verify that leading/trailing whitespaces are trimmed automatically."""
    correct = "Machine Learning"
    submitted = "   Machine Learning   "

    is_correct, ratio, _ = GradingService.evaluate_answer("short_answer", submitted, correct)
    assert is_correct is True
    assert ratio == 1


def test_short_answer_incorrect():
    """Verify that actual wrong answers are marked incorrect."""
    correct = "Python"
    submitted = "Java"

    is_correct, ratio, expl = GradingService.evaluate_answer("short_answer", submitted, correct)
    assert is_correct is False
    assert ratio == 0
    assert "Expected 'Python'" in expl


def test_true_false_evaluation():
    """Verify true/false evaluation handles casing safely."""
    is_correct, ratio, _ = GradingService.evaluate_answer("true_false", "true", "True")
    assert is_correct is True

    is_correct, ratio, _ = GradingService.evaluate_answer("true_false", "FALSE", "False")
    assert is_correct is True

    is_correct, ratio, _ = GradingService.evaluate_answer("true_false", "False", "True")
    assert is_correct is False
