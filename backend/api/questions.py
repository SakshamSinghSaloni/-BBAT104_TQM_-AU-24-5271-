"""
FastAPI route handlers for Question CRUD operations.
"""

from __future__ import annotations

import sqlite3
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.database import get_db
from backend.models import QuestionCreate, QuestionResponse, QuestionUpdate
from backend.services.question_service import QuestionService

router = APIRouter(tags=["Questions"])


@router.post(
    "/api/quizzes/{quiz_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_question(
    quiz_id: int, q_in: QuestionCreate, conn: sqlite3.Connection = Depends(get_db)
):
    """Add a question to a quiz with Q06 Pre-add Validation and Search Before Add."""
    service = QuestionService(conn)
    try:
        return service.add_question(
            quiz_id=quiz_id,
            question_text=q_in.question_text,
            question_type=q_in.question_type,
            options=q_in.options,
            correct_answer=q_in.correct_answer,
            points=q_in.points,
            order_index=q_in.order_index,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/api/quizzes/{quiz_id}/questions", response_model=List[QuestionResponse])
def list_questions(quiz_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """List all questions for a given quiz."""
    service = QuestionService(conn)
    try:
        return service.list_questions(quiz_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/api/questions/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Retrieve details of a single question."""
    service = QuestionService(conn)
    question = service.get_question(question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found."
        )
    return question


@router.put("/api/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int, q_in: QuestionUpdate, conn: sqlite3.Connection = Depends(get_db)
):
    """Update a question."""
    service = QuestionService(conn)
    updated = service.update_question(
        question_id=question_id,
        question_text=q_in.question_text,
        options=q_in.options,
        correct_answer=q_in.correct_answer,
        points=q_in.points,
        order_index=q_in.order_index,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found."
        )
    return updated


@router.delete("/api/questions/{question_id}", status_code=status.HTTP_200_OK)
def delete_question(question_id: int, conn: sqlite3.Connection = Depends(get_db)):
    """Delete a question."""
    service = QuestionService(conn)
    success = service.delete_question(question_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with ID {question_id} not found."
        )
    return {"message": f"Question {question_id} deleted successfully."}
