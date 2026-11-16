"""
SQLAlchemy 2.0 ORM Declarative Models for the Online Quiz System.

Enforces:
- Foreign key cascading deletes (ON DELETE CASCADE)
- Storage-level Unique Constraints (PKs, UNIQUE columns, composite unique constraints)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    """
    Teacher / Administrator account table.
    Unique constraint on email.
    Note: Students are ephemeral participants (stored in Participant table), not User accounts.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="teacher")
    created_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )


class Quiz(Base):
    """
    Quiz entity.
    Unique constraint on title.
    """
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
    updated_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    # Relationships with cascading deletes
    questions: Mapped[List[Question]] = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    sessions: Mapped[List[Session]] = relationship(
        "Session",
        back_populates="quiz",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Question(Base):
    """
    Question entity within a Quiz.
    CONSTRAINT uq_quiz_question_text UNIQUE (quiz_id, question_text).
    """
    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint("quiz_id", "question_text", name="uq_quiz_question_text"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), nullable=False, default="mcq")
    options_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correct_answer: Mapped[str] = mapped_column(String(500), nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    quiz: Mapped[Quiz] = relationship("Quiz", back_populates="questions")
    submissions: Mapped[List[Submission]] = relationship(
        "Submission",
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def options(self) -> Optional[List[str]]:
        if self.options_json:
            try:
                return json.loads(self.options_json)
            except Exception:
                return None
        return None

    @options.setter
    def options(self, val: Optional[List[str]]):
        if val is not None:
            self.options_json = json.dumps(val)
        else:
            self.options_json = None


class Session(Base):
    """
    Active or completed Quiz evaluation session.
    Unique constraint on session_code.
    """
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    quiz_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    started_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
    ended_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    quiz: Mapped[Quiz] = relationship("Quiz", back_populates="sessions")
    participants: Mapped[List[Participant]] = relationship(
        "Participant",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Participant(Base):
    """
    Student participant in a Quiz session.
    CONSTRAINT uq_session_participant UNIQUE (session_id, student_identifier).
    """
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint("session_id", "student_identifier", name="uq_session_participant"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_name: Mapped[str] = mapped_column(String(200), nullable=False)
    student_identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    joined_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    session: Mapped[Session] = relationship("Session", back_populates="participants")
    submissions: Mapped[List[Submission]] = relationship(
        "Submission",
        back_populates="participant",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Submission(Base):
    """
    Student answer submission for a Question.
    CONSTRAINT uq_participant_question UNIQUE (participant_id, question_id).
    """
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("participant_id", "question_id", name="uq_participant_question"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 1 = correct, 0 = incorrect
    points_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted_at: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    participant: Mapped[Participant] = relationship("Participant", back_populates="submissions")
    question: Mapped[Question] = relationship("Question", back_populates="submissions")
