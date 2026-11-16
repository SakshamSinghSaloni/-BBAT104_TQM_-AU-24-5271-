"""
Web page routes for Teacher Authentication (Login, Register, Logout).
"""

from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.middleware.auth import clear_session_cookie, get_current_user_optional, set_session_cookie
from backend.models import UserCreate
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Web Auth"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request, current_user=Depends(get_current_user_optional)):
    """Render the login form."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={"request": request, "current_user": None},
    )


@router.post("/login", response_class=HTMLResponse)
def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Authenticate teacher credentials from login form."""
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "request": request,
                "current_user": None,
                "flash_message": "Invalid email or password. Please verify your credentials.",
                "flash_type": "danger",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(response, user.id)
    return response


@router.get("/register", response_class=HTMLResponse)
def get_register(request: Request, current_user=Depends(get_current_user_optional)):
    """Render the instructor registration form."""
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={"request": request, "current_user": None},
    )


@router.post("/register", response_class=HTMLResponse)
def post_register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Create a new instructor account with duplicate email prevention."""
    auth_service = AuthService(db)
    try:
        user_create = UserCreate(name=name, email=email, password=password)
        user = auth_service.register_user(user_create)
    except (HTTPException, ValueError) as e:
        err_msg = e.detail if isinstance(e, HTTPException) else str(e)
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "request": request,
                "current_user": None,
                "flash_message": err_msg,
                "flash_type": "danger",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_session_cookie(response, user.id)
    return response


@router.post("/logout")
def post_logout():
    """Clear session cookie and redirect to landing page."""
    response = RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    clear_session_cookie(response)
    return response
