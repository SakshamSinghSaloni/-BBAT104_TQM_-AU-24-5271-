"""
Web page routes for Teacher Operations (Landing, Dashboard, Quiz CRUD, Question CRUD, Session Admin).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.middleware.auth import get_current_user_optional
from backend.models import QuestionCreate, QuizCreate, UserProfileUpdate
from backend.services.auth_service import AuthService
from backend.services.question_service import QuestionService
from backend.services.quiz_service import QuizService
from backend.services.session_service import SessionService

router = APIRouter(tags=["Teacher Web Pages"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def require_auth(current_user):
    """Helper to guard protected teacher web views."""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return None


@router.get("/", response_class=HTMLResponse)
def index_page(request: Request, current_user=Depends(get_current_user_optional)):
    """Application landing page."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "current_user": current_user},
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Teacher administrative dashboard."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    session_service = SessionService(db)

    quizzes = quiz_service.list_quizzes()
    sessions = session_service.list_all_sessions()

    total_quizzes = len(quizzes)
    active_sessions = sum(1 for s in sessions if s.status == "active")
    total_participants = sum(len(s.participants) for s in sessions)
    total_submissions = sum(
        sum(len(p.submissions) for p in s.participants) for s in sessions
    )

    stats = {
        "total_quizzes": total_quizzes,
        "active_sessions": active_sessions,
        "total_participants": total_participants,
        "total_submissions": total_submissions,
    }

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "sessions": sessions,
            "quizzes": quizzes,
        },
    )


@router.get("/quizzes", response_class=HTMLResponse)
def quizzes_page(
    request: Request,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Quiz library overview."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    quizzes = quiz_service.list_quizzes()
    return templates.TemplateResponse(
        request=request,
        name="quizzes/list.html",
        context={"request": request, "current_user": current_user, "quizzes": quizzes},
    )


@router.post("/quizzes", response_class=HTMLResponse)
def create_quiz_form(
    request: Request,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Create a new quiz with input sanitization and duplicate prevention."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    try:
        quiz_in = QuizCreate(title=title, description=description)
        quiz_service.create_quiz(title=quiz_in.title, description=quiz_in.description)
        return RedirectResponse(url="/quizzes", status_code=status.HTTP_303_SEE_OTHER)
    except (HTTPException, ValueError, ValidationError) as e:
        if isinstance(e, ValidationError):
            err_msg = "; ".join(err.get("msg", str(err)) for err in e.errors())
        else:
            err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        quizzes = quiz_service.list_quizzes()
        return templates.TemplateResponse(
            request=request,
            name="quizzes/list.html",
            context={
                "request": request,
                "current_user": current_user,
                "quizzes": quizzes,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/quizzes/{quiz_id}/delete")
def delete_quiz_form(
    quiz_id: int,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Delete a quiz via confirmed POST action."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    quiz_service.delete_quiz(quiz_id)
    return RedirectResponse(url="/quizzes", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/quizzes/{quiz_id}/questions", response_class=HTMLResponse)
def questions_page(
    quiz_id: int,
    request: Request,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Manage questions within a specific quiz."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    question_service = QuestionService(db)

    quiz = quiz_service.get_quiz(quiz_id)
    questions = question_service.list_questions(quiz_id)
    total_points = sum(q["points"] for q in questions)

    return templates.TemplateResponse(
        request=request,
        name="quizzes/questions.html",
        context={
            "request": request,
            "current_user": current_user,
            "quiz": quiz,
            "questions": questions,
            "total_points": total_points,
        },
    )


@router.post("/quizzes/{quiz_id}/questions", response_class=HTMLResponse)
def add_question_form(
    quiz_id: int,
    request: Request,
    question_text: str = Form(...),
    question_type: str = Form(...),
    points: int = Form(1),
    mcq_correct_idx: Optional[int] = Form(None),
    mcq_option_1: Optional[str] = Form(None),
    mcq_option_2: Optional[str] = Form(None),
    mcq_option_3: Optional[str] = Form(None),
    mcq_option_4: Optional[str] = Form(None),
    tf_answer: Optional[str] = Form(None),
    short_answer_text: Optional[str] = Form(None),
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Process add question form with dynamic type handling and duplicate prevention."""
    guard = require_auth(current_user)
    if guard:
        return guard

    quiz_service = QuizService(db)
    question_service = QuestionService(db)
    quiz = quiz_service.get_quiz(quiz_id)

    # Build options & correct answer depending on type
    options = None
    correct_answer = ""

    if question_type == "mcq":
        raw_options = [mcq_option_1, mcq_option_2, mcq_option_3, mcq_option_4]
        options = [opt.strip() for opt in raw_options if opt and opt.strip()]
        if mcq_correct_idx and 1 <= mcq_correct_idx <= len(options):
            correct_answer = options[mcq_correct_idx - 1]
        elif options:
            correct_answer = options[0]
    elif question_type == "true_false":
        options = ["True", "False"]
        correct_answer = tf_answer.strip() if tf_answer else "True"
    else:  # short_answer
        options = None
        correct_answer = short_answer_text.strip() if short_answer_text else ""

    try:
        q_create = QuestionCreate(
            question_text=question_text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            points=points,
        )
        question_service.add_question(
            quiz_id=quiz_id,
            question_text=q_create.question_text,
            question_type=q_create.question_type,
            options=q_create.options,
            correct_answer=q_create.correct_answer,
            points=q_create.points,
        )
        return RedirectResponse(
            url=f"/quizzes/{quiz_id}/questions",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except (HTTPException, ValueError, ValidationError) as e:
        if isinstance(e, ValidationError):
            err_msg = "; ".join(err.get("msg", str(err)) for err in e.errors())
        else:
            err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        questions = question_service.list_questions(quiz_id)
        total_points = sum(q["points"] for q in questions)
        return templates.TemplateResponse(
            request=request,
            name="quizzes/questions.html",
            context={
                "request": request,
                "current_user": current_user,
                "quiz": quiz,
                "questions": questions,
                "total_points": total_points,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/quizzes/{quiz_id}/questions/{question_id}/delete")
def delete_question_form(
    quiz_id: int,
    question_id: int,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Delete a question from a quiz."""
    guard = require_auth(current_user)
    if guard:
        return guard

    question_service = QuestionService(db)
    question_service.delete_question(question_id)
    return RedirectResponse(
        url=f"/quizzes/{quiz_id}/questions",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/quizzes/{quiz_id}/sessions")
def launch_session_action(
    quiz_id: int,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Launch a live assessment session for a quiz."""
    guard = require_auth(current_user)
    if guard:
        return guard

    session_service = SessionService(db)
    session = session_service.create_session(quiz_id)
    return RedirectResponse(
        url=f"/sessions/{session.id}/results",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/sessions/{session_id}/end")
def end_session_action(
    session_id: int,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """End a live session."""
    guard = require_auth(current_user)
    if guard:
        return guard

    session_service = SessionService(db)
    session_service.end_session(session_id)
    return RedirectResponse(
        url=f"/sessions/{session_id}/results",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/sessions/{session_id}/results", response_class=HTMLResponse)
def session_results_page(
    session_id: int,
    request: Request,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """View session analytics, leaderboard, and question stats."""
    guard = require_auth(current_user)
    if guard:
        return guard

    session_service = SessionService(db)
    results = session_service.get_session_results(session_id)
    return templates.TemplateResponse(
        request=request,
        name="sessions/results.html",
        context={"request": request, "current_user": current_user, "results": results},
    )


@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Teacher profile overview and account settings."""
    guard = require_auth(current_user)
    if guard:
        return guard

    auth_service = AuthService(db)
    stats = auth_service.get_teacher_activity_stats(current_user.id)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "request": request,
            "current_user": current_user,
            "stats": stats,
        },
    )


@router.post("/profile", response_class=HTMLResponse)
def update_profile_form(
    request: Request,
    name: str = Form(...),
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Update teacher display name with validation."""
    guard = require_auth(current_user)
    if guard:
        return guard

    auth_service = AuthService(db)
    try:
        profile_in = UserProfileUpdate(name=name)
        updated_user = auth_service.update_profile(current_user.id, profile_in)
        stats = auth_service.get_teacher_activity_stats(current_user.id)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "request": request,
                "current_user": updated_user,
                "stats": stats,
                "flash_message": "Profile display name updated successfully.",
                "flash_type": "success",
            },
        )
    except (HTTPException, ValueError, ValidationError) as e:
        if isinstance(e, ValidationError):
            err_msg = "; ".join(err.get("msg", str(err)) for err in e.errors())
        else:
            err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        stats = auth_service.get_teacher_activity_stats(current_user.id)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "request": request,
                "current_user": current_user,
                "stats": stats,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post("/profile/change-password", response_class=HTMLResponse)
def change_password_form(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user=Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Change instructor account password."""
    guard = require_auth(current_user)
    if guard:
        return guard

    auth_service = AuthService(db)
    stats = auth_service.get_teacher_activity_stats(current_user.id)

    if new_password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "request": request,
                "current_user": current_user,
                "stats": stats,
                "flash_message": "New password and confirmation do not match.",
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        auth_service.change_password(current_user.id, current_password, new_password)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "request": request,
                "current_user": current_user,
                "stats": stats,
                "flash_message": "Password updated successfully.",
                "flash_type": "success",
            },
        )
    except (HTTPException, ValueError, ValidationError) as e:
        err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "request": request,
                "current_user": current_user,
                "stats": stats,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
