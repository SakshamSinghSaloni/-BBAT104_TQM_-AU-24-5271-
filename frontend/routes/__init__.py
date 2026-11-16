"""
Frontend Web Routes Package.
Exports page routers for auth, teacher administrative workflows, and student assessment flows.
"""

from fastapi import APIRouter

from frontend.routes.auth_routes import router as auth_pages_router
from frontend.routes.student_routes import router as student_pages_router
from frontend.routes.teacher_routes import router as teacher_pages_router

web_router = APIRouter()
web_router.include_router(auth_pages_router)
web_router.include_router(teacher_pages_router)
web_router.include_router(student_pages_router)
