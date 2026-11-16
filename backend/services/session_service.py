"""
Session lifecycle and quiz administration service.
Manages quiz sessions, student participant entry, answer submission, auto-grading, and results aggregation.
"""

from __future__ import annotations

import json
import secrets
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from backend.db_models import Participant, Quiz, Session, Submission
from backend.models import AnswerSubmission, StudentQuizResult, SubmissionDetailResponse
from backend.repositories.question_repo import QuestionRepository
from backend.repositories.quiz_repo import QuizRepository
from backend.repositories.session_repo import SessionRepository
from backend.services.grading_service import GradingService


def generate_session_code() -> str:
    """Generate a high-entropy, human-friendly 6-character session code."""
    # Exclude ambiguous glyphs: 0, O, 1, I
    charset = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(charset) for _ in range(6))


class SessionService:
    def __init__(self, db: DbSession):
        self.db = db
        self.session_repo = SessionRepository(db)
        self.quiz_repo = QuizRepository(db)
        self.question_repo = QuestionRepository(db)

    def create_session(self, quiz_id: int) -> Session:
        """
        Launch a new session for a quiz.
        Generates a collision-free unique session code.
        """
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Quiz with ID {quiz_id} does not exist.",
            )

        # Generate unique code with collision retry
        for _ in range(10):
            code = generate_session_code()
            if not self.session_repo.get_session_by_code(code):
                return self.session_repo.create_session(quiz_id, code)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate a unique session code.",
        )

    def get_session(self, session_id: int) -> Session:
        """Retrieve session by primary key ID."""
        session = self.session_repo.get_session_by_id(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found.",
            )
        return session

    def get_session_by_code(self, session_code: str) -> Session:
        """Retrieve session by code."""
        session = self.session_repo.get_session_by_code(session_code)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with code '{session_code.upper()}' does not exist.",
            )
        return session

    def list_sessions_for_quiz(self, quiz_id: int) -> List[Session]:
        """List all sessions created for a specific quiz."""
        return self.session_repo.list_sessions_by_quiz(quiz_id)

    def list_all_sessions(self) -> List[Session]:
        """List all sessions ordered by start time desc."""
        return self.session_repo.list_all_sessions()

    def end_session(self, session_id: int) -> Session:
        """Terminate an active session."""
        session = self.session_repo.end_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found.",
            )
        return session

    def join_session(self, session_code: str, student_name: str, student_identifier: str) -> Participant:
        """
        Register a student into an active session.
        Validates session status and prevents duplicate participants.
        """
        clean_name = (student_name or "").strip()
        clean_id = (student_identifier or "").strip().upper()

        if not clean_name or not clean_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student name and Student ID cannot be empty.",
            )

        session = self.get_session_by_code(session_code)
        if session.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session '{session.session_code}' has ended and is no longer accepting participants.",
            )

        # Check if student has already joined this session
        existing = self.session_repo.get_participant_by_session_and_identifier(session.id, clean_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student ID '{clean_id}' has already joined session '{session.session_code}'.",
            )

        return self.session_repo.create_participant(
            session_id=session.id,
            student_name=clean_name,
            student_identifier=clean_id,
        )

    def get_questions_for_student(self, session_code: str) -> List[Dict[str, Any]]:
        """
        Retrieve questions for the student's test-taking view.
        Omits 'correct_answer' to preserve assessment integrity.
        """
        session = self.get_session_by_code(session_code)
        questions = self.question_repo.list_by_quiz_id(session.quiz_id)

        clean_questions = []
        for q in questions:
            options = None
            if q.options_json:
                try:
                    options = json.loads(q.options_json)
                except Exception:
                    options = []
            clean_questions.append({
                "id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": options,
                "points": q.points,
                "order_index": q.order_index,
            })
        return clean_questions

    def submit_answers(
        self,
        session_code: str,
        participant_id: int,
        answers: List[AnswerSubmission],
    ) -> StudentQuizResult:
        """Process, grade, and record student answers."""
        session = self.get_session_by_code(session_code)
        participant = self.session_repo.get_participant_by_id(participant_id)
        if not participant or participant.session_id != session.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant does not belong to this session.",
            )

        # Verify participant hasn't already submitted answers for this quiz
        existing_submissions = self.session_repo.list_submissions_by_participant(participant_id)
        if existing_submissions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Participant '{participant.student_identifier}' has already submitted this quiz.",
            )

        questions = {q.id: q for q in self.question_repo.list_by_quiz_id(session.quiz_id)}

        total_score = 0
        max_possible_score = sum(q.points for q in questions.values())
        details: List[SubmissionDetailResponse] = []

        # Map submitted answers by question_id
        submitted_map = {a.question_id: a.answer_text for a in answers}

        for q_id, question in questions.items():
            user_ans = submitted_map.get(q_id, "")
            is_correct, _, _ = GradingService.evaluate_answer(
                question.question_type, user_ans, question.correct_answer
            )
            points_awarded = question.points if is_correct else 0
            total_score += points_awarded

            # Persist submission record
            self.session_repo.create_submission(
                participant_id=participant_id,
                question_id=q_id,
                answer_text=user_ans,
                is_correct=1 if is_correct else 0,
                points_awarded=points_awarded,
            )

            details.append(
                SubmissionDetailResponse(
                    question_id=q_id,
                    question_text=question.question_text,
                    submitted_answer=user_ans,
                    correct_answer=question.correct_answer,
                    is_correct=is_correct,
                    points_awarded=points_awarded,
                    max_points=question.points,
                )
            )

        pct = round((total_score / max_possible_score * 100), 1) if max_possible_score > 0 else 0.0

        return StudentQuizResult(
            participant_id=participant.id,
            student_name=participant.student_name,
            student_identifier=participant.student_identifier,
            total_score=total_score,
            max_score=max_possible_score,
            percentage=pct,
            details=details,
        )

    def get_session_results(self, session_id: int) -> Dict[str, Any]:
        """
        Aggregate comprehensive analytics for an instructor review.
        Computes leaderboard, per-question accuracy, and summary statistics.
        """
        session = self.get_session(session_id)
        quiz = self.quiz_repo.get_by_id(session.quiz_id)
        participants = self.session_repo.list_participants_by_session(session_id)
        questions = self.question_repo.list_by_quiz_id(session.quiz_id)
        all_submissions = self.session_repo.list_submissions_by_session(session_id)

        # Build map of (participant_id, question_id) -> submission
        sub_map = {(s.participant_id, s.question_id): s for s in all_submissions}

        max_score = sum(q.points for q in questions)
        participant_results = []
        scores = []

        for p in participants:
            p_subs = [s for s in all_submissions if s.participant_id == p.id]
            has_submitted = len(p_subs) > 0
            p_score = sum(s.points_awarded for s in p_subs)
            scores.append(p_score)
            pct = round((p_score / max_score * 100), 1) if max_score > 0 else 0.0

            participant_results.append({
                "participant_id": p.id,
                "student_name": p.student_name,
                "student_identifier": p.student_identifier,
                "score": p_score,
                "max_score": max_score,
                "percentage": pct,
                "has_submitted": has_submitted,
                "joined_at": p.joined_at,
            })

        # Sort leaderboard descending by score
        participant_results.sort(key=lambda x: x["score"], reverse=True)

        # Question analytics
        question_stats = []
        for q in questions:
            q_subs = [s for s in all_submissions if s.question_id == q.id]
            total_answers = len(q_subs)
            correct_answers = sum(1 for s in q_subs if s.is_correct == 1)
            acc_rate = round((correct_answers / total_answers * 100), 1) if total_answers > 0 else 0.0
            question_stats.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "points": q.points,
                "total_responses": total_answers,
                "correct_responses": correct_answers,
                "accuracy_rate": acc_rate,
            })

        avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0

        return {
            "session_id": session.id,
            "session_code": session.session_code,
            "status": session.status,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "quiz_id": quiz.id if quiz else session.quiz_id,
            "quiz_title": quiz.title if quiz else "Unknown Quiz",
            "total_participants": len(participants),
            "total_submissions": len([p for p in participant_results if p["has_submitted"]]),
            "max_score": max_score,
            "average_score": avg_score,
            "highest_score": max(scores) if scores else 0,
            "leaderboard": participant_results,
            "question_stats": question_stats,
        }
