"""
Pydantic schemas and data validation models for the Online Quiz System.

Enforces:
- Input sanitization, bounds checking, and data validation
- Structural MCQ consistency checks before data reaches the storage layer.
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
    """Payload for creating a new quiz."""
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
    """Payload for creating a question."""
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

    @field_validator("question_text", "correct_answer")
    @classmethod
    def validate_non_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Field cannot be empty or whitespace only.")
            return cleaned
        return v

    @field_validator("options")
    @classmethod
    def validate_mcq_options(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            cleaned_options = [opt.strip() for opt in v if opt.strip()]
            if len(cleaned_options) < 2:
                raise ValueError("Multiple choice questions must have at least 2 non-empty options.")
            if len(cleaned_options) > 6:
                raise ValueError("Multiple choice questions cannot exceed 6 options.")
            return cleaned_options
        return v


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



# ==========================================
# USER & AUTH SCHEMAS
# ==========================================

class UserCreate(BaseModel):
    """Payload for registering a new teacher account."""
    email: str = Field(..., max_length=255, description="Unique email address")
    password: str = Field(..., min_length=6, max_length=128, description="Account password")
    name: str = Field(..., min_length=1, max_length=200, description="Display name")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("Invalid email format.")
        return cleaned

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Name cannot be blank.")
        return cleaned


class UserLogin(BaseModel):
    """Payload for logging into a teacher account."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()


class UserResponse(BaseModel):
    """User representation returned on successful authentication."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    created_at: str


class UserProfileUpdate(BaseModel):
    """Payload for updating user profile display name."""
    name: str = Field(..., min_length=1, max_length=100, description="Updated display name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Display name cannot be empty or whitespace only.")
        return cleaned


class UserPasswordChange(BaseModel):
    """Payload for changing instructor account password."""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")
    confirm_password: Optional[str] = Field(None, description="Password confirmation")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("New password must be at least 6 characters.")
        return v


# ==========================================
# SESSION & PARTICIPANT SCHEMAS
# ==========================================

class SessionCreate(BaseModel):
    """Payload to initiate a new quiz session."""
    quiz_id: int = Field(..., ge=1, description="Quiz to launch")


class SessionResponse(BaseModel):
    """Live assessment session representation."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    quiz_id: int
    session_code: str
    status: str
    started_at: str
    ended_at: Optional[str] = None
    quiz_title: Optional[str] = None
    participant_count: int = 0


class ParticipantJoin(BaseModel):
    """Student entry payload for joining an active session."""
    student_name: str = Field(..., min_length=1, max_length=200, description="Student's name")
    student_identifier: str = Field(..., min_length=1, max_length=100, description="Roll Number / ID")

    @field_validator("student_name", "student_identifier")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Student name and identifier cannot be blank.")
        return cleaned


class ParticipantResponse(BaseModel):
    """Participant record returned to student upon entry."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    student_name: str
    student_identifier: str
    joined_at: str


class AnswerSubmission(BaseModel):
    """Single answer submission within a quiz."""
    question_id: int = Field(..., ge=1)
    answer_text: str = Field(..., max_length=2000)

    @field_validator("answer_text")
    @classmethod
    def clean_answer(cls, v: str) -> str:
        return v.strip()


class QuizSubmissionPayload(BaseModel):
    """Batch answers submitted by a participant at the conclusion of a quiz."""
    participant_id: int = Field(..., ge=1)
    answers: List[AnswerSubmission] = Field(..., min_length=1)


class SubmissionDetailResponse(BaseModel):
    """Graded result for a single question."""
    question_id: int
    question_text: str
    submitted_answer: str
    correct_answer: str
    is_correct: bool
    points_awarded: int
    max_points: int


class StudentQuizResult(BaseModel):
    """Summary result returned to student after grading."""
    participant_id: int
    student_name: str
    student_identifier: str
    total_score: int
    max_score: int
    percentage: float
    details: List[SubmissionDetailResponse]

