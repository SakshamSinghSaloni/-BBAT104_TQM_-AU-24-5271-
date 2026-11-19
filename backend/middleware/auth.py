"""
Authentication middleware and session cookie management.
Uses itsdangerous URLSafeTimedSerializer to issue and verify tamper-proof signed session cookies.
"""

from __future__ import annotations

from typing import Optional
from fastapi import Depends, HTTPException, Request, Response, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from backend.config import COOKIE_SECURE, SECRET_KEY, SESSION_COOKIE_NAME, ACCESS_TOKEN_EXPIRE_MINUTES
from backend.database import get_db
from backend.db_models import User
from backend.repositories.user_repo import UserRepository

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="quiz-web-session")
_COOKIE_MAX_AGE = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # in seconds


def create_session_token(user_id: int) -> str:
    """Issue a signed session token for a given user ID."""
    return _serializer.dumps({"user_id": user_id})


def verify_session_token(token: str) -> Optional[int]:
    """Verify and unpack a session token; returns user_id or None if invalid/expired."""
    try:
        data = _serializer.loads(token, max_age=_COOKIE_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired, Exception):
        return None


def set_session_cookie(response: Response, user_id: int) -> None:
    """Set signed HTTP-only session cookie on the outgoing response."""
    token = create_session_token(user_id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,  # Configurable via COOKIE_SECURE env; default False for local dev
    )


def clear_session_cookie(response: Response) -> None:
    """Delete session cookie to log out user."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
    )


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Retrieve the logged-in User if session cookie is present and valid; else None."""
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        # Also support Authorization header Bearer token if passed by API clients
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        return None

    user_id = verify_session_token(token)
    if user_id is None:
        return None

    repo = UserRepository(db)
    return repo.get_by_id(user_id)


def get_current_user(
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """
    Mandatory dependency for protected routes.
    Raises HTTP 401 for API requests if unauthenticated.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Cookie"},
        )
    return user
