"""
SQLAlchemy Data Access Repository for Quiz entities.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db_models import Question, Quiz


class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, quiz: Quiz) -> Dict[str, Any]:
        """Convert a Quiz ORM model instance to dictionary representation."""
        q_count = len(quiz.questions) if quiz.questions is not None else 0
        return {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "created_at": quiz.created_at,
            "updated_at": quiz.updated_at,
            "question_count": q_count,
            "questions": [q.id for q in quiz.questions] if quiz.questions else [],
        }

    def create(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        quiz = Quiz(
            title=title.strip(),
            description=description.strip() if description else None,
            created_at=now,
            updated_at=now,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return self._to_dict(quiz)

    def get_by_id(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        quiz = self.db.scalars(stmt).first()
        if not quiz:
            return None
        return self._to_dict(quiz)

    def list_all(self) -> List[Dict[str, Any]]:
        stmt = select(Quiz).order_by(Quiz.id.desc())
        quizzes = self.db.scalars(stmt).all()
        return [self._to_dict(q) for q in quizzes]

    def find_by_title(self, title: str) -> List[Dict[str, Any]]:
        """Find quiz by title to prevent duplicate titles (case-insensitive)."""
        clean = title.strip()
        stmt = select(Quiz).where(func.lower(Quiz.title) == func.lower(clean))
        quizzes = self.db.scalars(stmt).all()
        return [self._to_dict(q) for q in quizzes]

    def update(
        self, quiz_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        quiz = self.db.get(Quiz, quiz_id)
        if not quiz:
            return None

        if title is not None:
            quiz.title = title.strip()
        if description is not None:
            quiz.description = description.strip() if description else None

        quiz.updated_at = datetime.now(timezone.utc).isoformat()
        self.db.commit()
        self.db.refresh(quiz)
        return self._to_dict(quiz)

    def delete(self, quiz_id: int) -> bool:
        quiz = self.db.get(Quiz, quiz_id)
        if not quiz:
            return False
        self.db.delete(quiz)
        self.db.commit()
        return True
