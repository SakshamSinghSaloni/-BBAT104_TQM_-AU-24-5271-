"""
Auto-grading and answer evaluation service for the Online Quiz System.

Enforces:
- Normalized, whitespace-trimmed, case-insensitive comparison for short_answer and true_false questions.
- Exact option matching for multiple-choice questions (mcq).
- Zero-defect grading calculation (customer focus / error prevention).
"""

from __future__ import annotations

from typing import Tuple


class GradingService:
    @staticmethod
    def evaluate_answer(
        question_type: str, submitted_answer: str, correct_answer: str
    ) -> Tuple[bool, int, str]:
        """
        Evaluate a submitted answer against the correct answer.

        Returns:
            Tuple[is_correct: bool, points_ratio: int (0 or 1), explanation: str]
        """
        clean_submitted = (submitted_answer or "").strip()
        clean_correct = (correct_answer or "").strip()

        if not clean_submitted:
            return False, 0, "No answer provided."

        if question_type == "short_answer":
            # Case-insensitive, whitespace-normalized evaluation
            is_match = clean_submitted.casefold() == clean_correct.casefold()
            explanation = "Correct" if is_match else f"Expected '{clean_correct}'"
            return is_match, (1 if is_match else 0), explanation

        elif question_type == "true_false":
            # Normalized boolean comparison
            is_match = clean_submitted.casefold() == clean_correct.casefold()
            explanation = "Correct" if is_match else f"Expected '{clean_correct}'"
            return is_match, (1 if is_match else 0), explanation

        elif question_type == "mcq":
            # Strict option match (case-insensitive for safety)
            is_match = clean_submitted.strip().casefold() == clean_correct.strip().casefold()
            explanation = "Correct" if is_match else f"Expected '{clean_correct}'"
            return is_match, (1 if is_match else 0), explanation

        else:
            # Fallback for generic question types
            is_match = clean_submitted.casefold() == clean_correct.casefold()
            return is_match, (1 if is_match else 0), "Evaluated"
