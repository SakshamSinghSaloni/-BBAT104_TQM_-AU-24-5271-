"""
SQLAlchemy Data Access Repository for Question entities.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db_models import Question


class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, q: Question) -> Dict[str, Any]:
        """Convert a Question ORM model instance to dictionary representation."""
        opts = None
        if q.options_json:
            try:
                opts = json.loads(q.options_json)
            except Exception:
                opts = None

        return {
            "id": q.id,
            "quiz_id": q.quiz_id,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": opts,
            "correct_answer": q.correct_answer,
            "points": q.points,
            "order_index": q.order_index,
            "created_at": q.created_at,
        }

    def create(
        self,
        quiz_id: int,
        question_text: str,
        question_type: str,
        options: Optional[List[str]],
        correct_answer: str,
        points: int = 1,
        order_index: int = 0,
    ) -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        options_json = json.dumps(options) if options is not None else None

        question = Question(
            quiz_id=quiz_id,
            question_text=question_text.strip(),
            question_type=question_type,
            options_json=options_json,
            correct_answer=correct_answer.strip(),
            points=points,
            order_index=order_index,
            created_at=now,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return self._to_dict(question)

    def get_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        question = self.db.get(Question, question_id)
        if not question:
            return None
        return self._to_dict(question)

    def list_by_quiz(self, quiz_id: int) -> List[Dict[str, Any]]:
        stmt = (
            select(Question)
            .where(Question.quiz_id == quiz_id)
            .order_by(Question.order_index.asc(), Question.id.asc())
        )
        questions = self.db.scalars(stmt).all()
        return [self._to_dict(q) for q in questions]

    def find_duplicate_in_quiz(self, quiz_id: int, question_text: str) -> List[Dict[str, Any]]:
        """Find question by text in a quiz to prevent duplicate prompts."""
        clean_text = question_text.strip()
        stmt = select(Question).where(
            Question.quiz_id == quiz_id,
            func.lower(func.trim(Question.question_text)) == func.lower(clean_text),
        )
        questions = self.db.scalars(stmt).all()
        return [self._to_dict(q) for q in questions]

    def update(
        self,
        question_id: int,
        question_text: Optional[str] = None,
        options: Optional[List[str]] = None,
        correct_answer: Optional[str] = None,
        points: Optional[int] = None,
        order_index: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        question = self.db.get(Question, question_id)
        if not question:
            return None

        if question_text is not None:
            question.question_text = question_text.strip()
        if options is not None:
            question.options_json = json.dumps(options)
        if correct_answer is not None:
            question.correct_answer = correct_answer.strip()
        if points is not None:
            question.points = points
        if order_index is not None:
            question.order_index = order_index

        self.db.commit()
        self.db.refresh(question)
        return self._to_dict(question)

    def delete(self, question_id: int) -> bool:
        question = self.db.get(Question, question_id)
        if not question:
            return False
        self.db.delete(question)
        self.db.commit()
        return True
