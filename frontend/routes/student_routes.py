"""
Web page routes for Student Quiz Operations (Join, Take, Results).
Designed for seamless, friction-free participation without mandatory student accounts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import AnswerSubmission, StudentQuizResult, SubmissionDetailResponse
from backend.services.grading_service import GradingService
from backend.services.session_service import SessionService

router = APIRouter(tags=["Student Web Pages"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/join", response_class=HTMLResponse)
def get_join(request: Request, code: Optional[str] = Query(None)):
    """Render the student entry screen."""
    return templates.TemplateResponse(
        request=request,
        name="student/join.html",
        context={"request": request, "initial_code": code, "current_user": None},
    )


@router.post("/join", response_class=HTMLResponse)
def post_join(
    request: Request,
    session_code: str = Form(...),
    student_name: str = Form(...),
    student_identifier: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Register student into the assessment room.
    Validates session status and prevents duplicate participants.
    """
    session_service = SessionService(db)
    clean_code = session_code.strip().upper()

    try:
        participant = session_service.join_session(
            session_code=clean_code,
            student_name=student_name,
            student_identifier=student_identifier,
        )
        return RedirectResponse(
            url=f"/session/{clean_code}/take?participant_id={participant.id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except (HTTPException, ValueError) as e:
        err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        return templates.TemplateResponse(
            request=request,
            name="student/join.html",
            context={
                "request": request,
                "initial_code": clean_code,
                "current_user": None,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get("/session/{session_code}/take", response_class=HTMLResponse)
def get_take_quiz(
    session_code: str,
    request: Request,
    participant_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Render the assessment interface for an active session."""
    session_service = SessionService(db)
    clean_code = session_code.strip().upper()

    session = session_service.get_session_by_code(clean_code)
    participant = session_service.session_repo.get_participant_by_id(participant_id)

    if not participant or participant.session_id != session.id:
        return RedirectResponse(url="/join", status_code=status.HTTP_303_SEE_OTHER)

    # Check if participant has already submitted answers
    existing_submissions = session_service.session_repo.list_submissions_by_participant(participant_id)
    if existing_submissions:
        return RedirectResponse(
            url=f"/session/{clean_code}/results?participant_id={participant_id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    quiz = session.quiz
    questions = session_service.get_questions_for_student(clean_code)

    return templates.TemplateResponse(
        request=request,
        name="student/take.html",
        context={
            "request": request,
            "current_user": None,
            "session": session,
            "quiz": quiz,
            "participant": participant,
            "questions": questions,
        },
    )


@router.post("/session/{session_code}/submit")
async def post_submit_quiz(
    session_code: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Process and auto-grade submitted test answers."""
    session_service = SessionService(db)
    clean_code = session_code.strip().upper()

    form_data = await request.form()
    participant_id_str = form_data.get("participant_id")
    if not participant_id_str:
        return RedirectResponse(url="/join", status_code=status.HTTP_303_SEE_OTHER)

    participant_id = int(participant_id_str)
    session = session_service.get_session_by_code(clean_code)
    questions = session_service.question_repo.list_by_quiz(session.quiz_id)

    answers: list[AnswerSubmission] = []
    for q in questions:
        ans_key = f"q_{q['id']}"
        ans_val = str(form_data.get(ans_key, "")).strip()
        answers.append(AnswerSubmission(question_id=q["id"], answer_text=ans_val))

    try:
        session_service.submit_answers(
            session_code=clean_code,
            participant_id=participant_id,
            answers=answers,
        )
    except HTTPException as e:
        # If duplicate submission, still send to results view
        if e.status_code == status.HTTP_409_CONFLICT:
            return RedirectResponse(
                url=f"/session/{clean_code}/results?participant_id={participant_id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        raise e

    return RedirectResponse(
        url=f"/session/{clean_code}/results?participant_id={participant_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/session/{session_code}/results", response_class=HTMLResponse)
def get_student_results(
    session_code: str,
    request: Request,
    participant_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """Display individual scorecard and question answer breakdown for a participant."""
    session_service = SessionService(db)
    clean_code = session_code.strip().upper()

    session = session_service.get_session_by_code(clean_code)
    participant = session_service.session_repo.get_participant_by_id(participant_id)

    if not participant or participant.session_id != session.id:
        return RedirectResponse(url="/join", status_code=status.HTTP_303_SEE_OTHER)

    submissions = session_service.session_repo.list_submissions_by_participant(participant_id)
    questions = session_service.question_repo.list_by_quiz(session.quiz_id)
    q_map = {q["id"]: q for q in questions}

    total_score = 0
    max_score = sum(q["points"] for q in questions)
    details: list[SubmissionDetailResponse] = []

    for s in submissions:
        q = q_map.get(s.question_id)
        if q:
            is_correct = bool(s.is_correct)
            total_score += s.points_awarded
            details.append(
                SubmissionDetailResponse(
                    question_id=q["id"],
                    question_text=q["question_text"],
                    submitted_answer=s.answer_text,
                    correct_answer=q["correct_answer"],
                    is_correct=is_correct,
                    points_awarded=s.points_awarded,
                    max_points=q["points"],
                )
            )

    pct = round((total_score / max_score * 100), 1) if max_score > 0 else 0.0

    result = StudentQuizResult(
        participant_id=participant.id,
        student_name=participant.student_name,
        student_identifier=participant.student_identifier,
        total_score=total_score,
        max_score=max_score,
        percentage=pct,
        details=details,
    )

    return templates.TemplateResponse(
        request=request,
        name="student/results.html",
        context={
            "request": request,
            "current_user": None,
            "session_code": clean_code,
            "result": result,
        },
    )
