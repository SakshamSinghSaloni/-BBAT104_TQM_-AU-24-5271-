"""
Authentication and identity service.
Handles password hashing (bcrypt), user registration, and credential validation.
"""

from __future__ import annotations

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.db_models import Participant, Quiz, Session as QuizSession, Submission, User
from backend.models import UserCreate, UserProfileUpdate
from backend.repositories.user_repo import UserRepository


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register_user(self, data: UserCreate) -> User:
        """Register a new user account with duplicate email validation."""
        email = data.email.strip().lower()

        # Check for existing account
        existing = self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"An account with email '{email}' already exists.",
            )

        password_hash = hash_password(data.password)
        return self.repo.create(
            email=email,
            password_hash=password_hash,
            name=data.name.strip(),
            role="teacher",
        )

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Verify user credentials; returns User object if valid, None otherwise."""
        user = self.repo.get_by_email(email.strip().lower())
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve user by ID."""
        return self.repo.get_by_id(user_id)

    def update_profile(self, user_id: int, data: UserProfileUpdate) -> User:
        """Update user display name with sanitization and Tier 2 validation."""
        name = data.name.strip()
        if not name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Display name cannot be empty or whitespace only.",
            )
        user = self.repo.update_profile(user_id, name)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    def change_password(self, user_id: int, current_pwd: str, new_pwd: str) -> bool:
        """Change user password after verifying current credentials."""
        user = self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        if not verify_password(current_pwd, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect.",
            )
        if len(new_pwd) < 6:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="New password must be at least 6 characters long.",
            )
        new_hash = hash_password(new_pwd)
        self.repo.update_password(user_id, new_hash)
        return True

    def get_teacher_activity_stats(self, user_id: int) -> dict:
        """Compile activity and impact statistics for instructor dashboard and profile."""
        total_quizzes = self.db.query(Quiz).count()
        total_sessions = self.db.query(QuizSession).count()
        active_sessions = self.db.query(QuizSession).filter(QuizSession.status == "active").count()
        total_participants = self.db.query(Participant).count()
        total_submissions = self.db.query(Submission).count()
        return {
            "total_quizzes": total_quizzes,
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_participants": total_participants,
            "total_submissions": total_submissions,
        }
