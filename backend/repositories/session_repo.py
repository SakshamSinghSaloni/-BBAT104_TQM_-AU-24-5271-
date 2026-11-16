"""
Repository for Session, Participant, and Submission persistence using SQLAlchemy 2.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from backend.db_models import Session, Participant, Submission


class SessionRepository:
    def __init__(self, db: DbSession):
        self.db = db

    # =========================================================================
    # Session Operations
    # =========================================================================
    def create_session(self, quiz_id: int, session_code: str) -> Session:
        now = datetime.now(timezone.utc).isoformat()
        session = Session(
            quiz_id=quiz_id,
            session_code=session_code.strip().upper(),
            status="active",
            started_at=now,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session_by_id(self, session_id: int) -> Session | None:
        return self.db.get(Session, session_id)

    def get_session_by_code(self, session_code: str) -> Session | None:
        stmt = select(Session).where(Session.session_code == session_code.strip().upper())
        return self.db.execute(stmt).scalar_one_or_none()

    def list_sessions_by_quiz(self, quiz_id: int) -> list[Session]:
        stmt = select(Session).where(Session.quiz_id == quiz_id).order_by(Session.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def list_all_sessions(self) -> list[Session]:
        stmt = select(Session).order_by(Session.id.desc())
        return list(self.db.execute(stmt).scalars().all())

    def end_session(self, session_id: int) -> Session | None:
        session = self.get_session_by_id(session_id)
        if not session:
            return None
        session.status = "ended"
        session.ended_at = datetime.now(timezone.utc).isoformat()
        self.db.commit()
        self.db.refresh(session)
        return session

    # =========================================================================
    # Participant Operations
    # =========================================================================
    def create_participant(self, session_id: int, student_name: str, student_identifier: str) -> Participant:
        now = datetime.now(timezone.utc).isoformat()
        participant = Participant(
            session_id=session_id,
            student_name=student_name.strip(),
            student_identifier=student_identifier.strip().upper(),
            joined_at=now,
        )
        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)
        return participant

    def get_participant_by_session_and_identifier(
        self, session_id: int, student_identifier: str
    ) -> Participant | None:
        stmt = select(Participant).where(
            Participant.session_id == session_id,
            Participant.student_identifier == student_identifier.strip().upper(),
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_participant_by_id(self, participant_id: int) -> Participant | None:
        return self.db.get(Participant, participant_id)

    def list_participants_by_session(self, session_id: int) -> list[Participant]:
        stmt = select(Participant).where(Participant.session_id == session_id).order_by(Participant.id.asc())
        return list(self.db.execute(stmt).scalars().all())

    # =========================================================================
    # Submission Operations
    # =========================================================================
    def create_submission(
        self,
        participant_id: int,
        question_id: int,
        answer_text: str,
        is_correct: int,
        points_awarded: int,
    ) -> Submission:
        now = datetime.now(timezone.utc).isoformat()
        submission = Submission(
            participant_id=participant_id,
            question_id=question_id,
            answer_text=answer_text.strip(),
            is_correct=is_correct,
            points_awarded=points_awarded,
            submitted_at=now,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_submission(self, participant_id: int, question_id: int) -> Submission | None:
        stmt = select(Submission).where(
            Submission.participant_id == participant_id,
            Submission.question_id == question_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_submissions_by_participant(self, participant_id: int) -> list[Submission]:
        stmt = select(Submission).where(Submission.participant_id == participant_id).order_by(Submission.question_id.asc())
        return list(self.db.execute(stmt).scalars().all())

    def list_submissions_by_session(self, session_id: int) -> list[Submission]:
        stmt = (
            select(Submission)
            .join(Participant, Submission.participant_id == Participant.id)
            .where(Participant.session_id == session_id)
            .order_by(Submission.id.asc())
        )
        return list(self.db.execute(stmt).scalars().all())
