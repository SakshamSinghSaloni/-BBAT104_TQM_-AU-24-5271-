"""
REST API endpoints for Teacher/User Authentication.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.middleware.auth import clear_session_cookie, get_current_user, set_session_cookie
from backend.models import UserCreate, UserLogin, UserResponse
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, response: Response, db: Session = Depends(get_db)):
    """
    Register a new teacher/admin account.
    Enforces unique email address verification.
    """
    service = AuthService(db)
    user = service.register_user(payload)
    set_session_cookie(response, user.id)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
    )


@router.post("/login", response_model=UserResponse)
def login(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Log into a teacher account using email and password.
    Sets signed HTTP-only session cookie.
    """
    service = AuthService(db)
    user = service.authenticate_user(payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    set_session_cookie(response, user.id)
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
    )


@router.post("/logout")
def logout(response: Response):
    """Clear session cookie and log out."""
    clear_session_cookie(response)
    return {"message": "Successfully logged out."}


@router.get("/me", response_model=UserResponse)
def get_me(user=Depends(get_current_user)):
    """Retrieve currently authenticated user profile."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        created_at=user.created_at,
    )
