"""
Business logic service for Question management.

Enforces:
- Parent Quiz existence check
- Q06 Feature 3: Search Before Add (searches for identical question text in the same quiz)
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional
from backend.repositories.question_repo import QuestionRepository
from backend.repositories.quiz_repo import QuizRepository


class QuestionService:
    def __init__(self, conn: sqlite3.Connection):
        self.question_repo = QuestionRepository(conn)
        self.quiz_repo = QuizRepository(conn)

    def add_question(
        self,
        quiz_id: int,
        question_text: str,
        question_type: str,
        options: Optional[List[str]],
        correct_answer: str,
        points: int = 1,
        order_index: int = 0,
    ) -> Dict[str, Any]:
        """
        Add a question to a quiz.
        Validates parent quiz existence and performs Q06 Search Before Add.
        """
        # 1. Verify parent quiz exists
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            raise KeyError(f"Quiz with ID {quiz_id} not found.")

        # 2. Q06 Feature 3: Search Before Add (Strict Duplicate Prevention)
        duplicate_matches = self.question_repo.find_duplicate_in_quiz(quiz_id, question_text)
        if duplicate_matches:
            raise ValueError(
                f"An identical question already exists in this quiz (Question #{duplicate_matches[0]['id']}). Duplicate questions are not allowed."
            )

        return self.question_repo.create(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            points=points,
            order_index=order_index,
        )

    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        return self.question_repo.get_by_id(question_id)

    def list_questions(self, quiz_id: int) -> List[Dict[str, Any]]:
        # Verify quiz exists
        if not self.quiz_repo.get_by_id(quiz_id):
            raise KeyError(f"Quiz with ID {quiz_id} not found.")
        return self.question_repo.list_by_quiz(quiz_id)

    def update_question(
        self,
        question_id: int,
        question_text: Optional[str] = None,
        options: Optional[List[str]] = None,
        correct_answer: Optional[str] = None,
        points: Optional[int] = None,
        order_index: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        existing = self.question_repo.get_by_id(question_id)
        if not existing:
            return None

        # Q06 Feature 3: Search Before Add (Strict Duplicate Prevention on question update)
        if question_text is not None and question_text.strip().lower() != existing["question_text"].strip().lower():
            duplicates = self.question_repo.find_duplicate_in_quiz(existing["quiz_id"], question_text)
            other_duplicates = [d for d in duplicates if d["id"] != question_id]
            if other_duplicates:
                raise ValueError(
                    f"An identical question already exists in this quiz (Question #{other_duplicates[0]['id']}). Duplicate questions are not allowed."
                )

        # Q06 Feature 2: Pre-add Validation (cross-field consistency on MCQ update)
        final_options = options if options is not None else existing.get("options")
        final_answer = correct_answer if correct_answer is not None else existing["correct_answer"]
        question_type = existing.get("question_type", "mcq")
        if question_type == "mcq" and final_options:
            if final_answer not in final_options:
                raise ValueError(
                    f"Correct answer '{final_answer}' must be present in the options: {final_options}"
                )

        return self.question_repo.update(
            question_id=question_id,
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            points=points,
            order_index=order_index,
        )

    def delete_question(self, question_id: int) -> bool:
        return self.question_repo.delete(question_id)
