"""
FastAPI route handlers for Quiz CRUD operations.
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import QuizCreate, QuizResponse, QuizUpdate
from backend.services.quiz_service import QuizService

router = APIRouter(prefix="/api/quizzes", tags=["Quizzes"])


@router.post("", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(quiz_in: QuizCreate, db: Session = Depends(get_db)):
    """Create a new quiz with input validation and duplicate prevention."""
    service = QuizService(db)
    try:
        return service.create_quiz(title=quiz_in.title, description=quiz_in.description)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("", response_model=List[QuizResponse])
def list_quizzes(db: Session = Depends(get_db)):
    """List all quizzes."""
    service = QuizService(db)
    return service.list_quizzes()


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a specific quiz by ID."""
    service = QuizService(db)
    quiz = service.get_quiz(quiz_id)
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found.",
        )
    return quiz


@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: int, quiz_in: QuizUpdate, db: Session = Depends(get_db)
):
    """Update quiz metadata."""
    service = QuizService(db)
    try:
        updated = service.update_quiz(
            quiz_id=quiz_id, title=quiz_in.title, description=quiz_in.description
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found.",
        )
    return updated


@router.delete("/{quiz_id}", status_code=status.HTTP_200_OK)
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Delete a quiz and cascade-delete all its questions."""
    service = QuizService(db)
    success = service.delete_quiz(quiz_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found.",
        )
    return {"message": f"Quiz {quiz_id} deleted successfully."}
