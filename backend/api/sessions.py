"""
REST API endpoints for Quiz Sessions, Student Join, and Answer Submission.
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.middleware.auth import get_current_user
from backend.models import (
    ParticipantJoin,
    ParticipantResponse,
    QuizSubmissionPayload,
    SessionCreate,
    SessionResponse,
    StudentQuizResult,
)
from backend.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """
    Teacher launches an assessment session for a quiz.
    Generates an authenticated unique 6-character session code.
    """
    service = SessionService(db)
    session = service.create_session(payload.quiz_id)
    return SessionResponse(
        id=session.id,
        quiz_id=session.quiz_id,
        session_code=session.session_code,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        participant_count=len(session.participants),
    )


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """List all quiz sessions created in the system."""
    service = SessionService(db)
    sessions = service.list_all_sessions()
    return [
        SessionResponse(
            id=s.id,
            quiz_id=s.quiz_id,
            session_code=s.session_code,
            status=s.status,
            started_at=s.started_at,
            ended_at=s.ended_at,
            quiz_title=s.quiz.title if s.quiz else None,
            participant_count=len(s.participants),
        )
        for s in sessions
    ]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):
    """Retrieve details for a specific session."""
    service = SessionService(db)
    session = service.get_session(session_id)
    return SessionResponse(
        id=session.id,
        quiz_id=session.quiz_id,
        session_code=session.session_code,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        quiz_title=session.quiz.title if session.quiz else None,
        participant_count=len(session.participants),
    )


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Terminate an active assessment session."""
    service = SessionService(db)
    session = service.end_session(session_id)
    return SessionResponse(
        id=session.id,
        quiz_id=session.quiz_id,
        session_code=session.session_code,
        status=session.status,
        started_at=session.started_at,
        ended_at=session.ended_at,
        participant_count=len(session.participants),
    )


@router.get("/{session_id}/results", response_model=Dict[str, Any])
def get_session_results(
    session_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Retrieve complete analytics and leaderboard for a session."""
    service = SessionService(db)
    return service.get_session_results(session_id)


# =============================================================================
# Student Flow Endpoints (Ephemeral / No Account Required)
# =============================================================================

@router.post("/{session_code}/join", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
def join_session(session_code: str, payload: ParticipantJoin, db: Session = Depends(get_db)):
    """
    Student joins an active session by session code.
    Validates session status and prevents duplicate participants.
    """
    service = SessionService(db)
    participant = service.join_session(
        session_code=session_code,
        student_name=payload.student_name,
        student_identifier=payload.student_identifier,
    )
    return ParticipantResponse(
        id=participant.id,
        session_id=participant.session_id,
        student_name=participant.student_name,
        student_identifier=participant.student_identifier,
        joined_at=participant.joined_at,
    )


@router.get("/{session_code}/questions", response_model=List[Dict[str, Any]])
def get_session_questions(session_code: str, db: Session = Depends(get_db)):
    """Retrieve quiz questions for an active session (excluding correct answers)."""
    service = SessionService(db)
    return service.get_questions_for_student(session_code)


@router.post("/{session_code}/submit", response_model=StudentQuizResult)
def submit_quiz_answers(
    session_code: str,
    payload: QuizSubmissionPayload,
    db: Session = Depends(get_db),
):
    """
    Submit and auto-grade all answers for a participant.
    Prevents duplicate submissions.
    """
    service = SessionService(db)
    return service.submit_answers(
        session_code=session_code,
        participant_id=payload.participant_id,
        answers=payload.answers,
    )
