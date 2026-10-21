"""
Business logic service for Quiz management.

Enforces:
- Q06 Feature 3: Search Before Add (identifies duplicate or near-duplicate titles)
"""

from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional
from backend.repositories.quiz_repo import QuizRepository


class QuizService:
    def __init__(self, conn: sqlite3.Connection):
        self.repo = QuizRepository(conn)

    def create_quiz(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new quiz record.
        Includes Q06 Search Before Add check to audit duplicate titles.
        """
        # Q06 Feature 3: Search Before Add (Strict Duplicate Prevention)
        existing = self.repo.find_by_title(title)
        if existing:
            raise ValueError(
                f"A quiz with title '{title}' already exists (Quiz #{existing[0]['id']}). Duplicate quizzes are not allowed."
            )

        return self.repo.create(title=title, description=description)

    def get_quiz(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_id(quiz_id)

    def list_quizzes(self) -> List[Dict[str, Any]]:
        return self.repo.list_all()

    def update_quiz(
        self, quiz_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        return self.repo.update(quiz_id, title=title, description=description)

    def delete_quiz(self, quiz_id: int) -> bool:
        return self.repo.delete(quiz_id)
