"""
Pydantic schemas and data validation models for the Online Quiz System.

Enforces:
- Q06 Feature 2: Pre-add Validation (input sanitization, bounds checking,
  structural MCQ consistency checks before data reaches the storage layer).
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# Supported question types
QuestionType = Literal["mcq", "true_false", "short_answer"]


# ==========================================
# QUIZ SCHEMAS
# ==========================================

class QuizCreate(BaseModel):
    """Payload for creating a new quiz (with Q06 Pre-add Validation)."""
    title: str = Field(..., max_length=200, description="Title of the quiz")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Quiz title cannot be empty or whitespace only.")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            return cleaned if cleaned else None
        return None


class QuizUpdate(BaseModel):
    """Payload for modifying an existing quiz."""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Quiz title cannot be empty or whitespace only.")
            return cleaned
        return None


class QuizResponse(BaseModel):
    """Quiz representation returned to clients."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    question_count: int = 0
    created_at: str
    updated_at: str


# ==========================================
# QUESTION SCHEMAS
# ==========================================

class QuestionCreate(BaseModel):
    """Payload for creating a question (with Q06 Pre-add Validation)."""
    question_text: str = Field(..., max_length=2000, description="The prompt of the question")
    question_type: QuestionType = Field(default="mcq", description="Question category")
    options: Optional[List[str]] = Field(default=None, description="List of options for MCQ")
    correct_answer: str = Field(..., max_length=500, description="Correct answer text")
    points: int = Field(default=1, ge=1, le=100, description="Points awarded")
    order_index: int = Field(default=0, ge=0, description="Ordering index in the quiz")

    @field_validator("question_text", "correct_answer")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Field cannot be empty or whitespace only.")
        return cleaned

    @field_validator("options")
    @classmethod
    def validate_mcq_options(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        if v is not None:
            cleaned_options = [opt.strip() for opt in v if opt.strip()]
            if len(cleaned_options) < 2:
                raise ValueError("Multiple choice questions must have at least 2 non-empty options.")
            if len(cleaned_options) > 6:
                raise ValueError("Multiple choice questions cannot exceed 6 options.")
            return cleaned_options
        return v

    def model_post_init(self, __context) -> None:
        """Validate that correct_answer is one of the options for MCQ."""
        if self.question_type == "mcq":
            if not self.options:
                raise ValueError("Options list is required for MCQ questions.")
            if self.correct_answer not in self.options:
                raise ValueError(
                    f"Correct answer '{self.correct_answer}' must be present in the options: {self.options}"
                )


class QuestionUpdate(BaseModel):
    """Payload for editing a question."""
    question_text: Optional[str] = Field(None, max_length=2000)
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = Field(None, max_length=500)
    points: Optional[int] = Field(None, ge=1, le=100)
    order_index: Optional[int] = Field(None, ge=0)


class QuestionResponse(BaseModel):
    """Question representation returned to clients."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    points: int
    order_index: int
    created_at: str
