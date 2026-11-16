"""
Authentication and identity service.
Handles password hashing (bcrypt), user registration, and credential validation.
"""

from __future__ import annotations

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.db_models import User
from backend.models import UserCreate
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
