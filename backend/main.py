"""
FastAPI application entry point for the Unified Online Quiz Web Platform.

Configures:
- Lifespan database initialization
- Static file serving (/static)
- CORS middleware
- API route registration (/api/quizzes, /api/questions, /api/auth, /api/sessions)
- Web route registration (SSR Jinja2 templates for auth, teacher, student)
- OpenAPI / Swagger documentation (/docs)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import auth, questions, quizzes, sessions
from backend.database import init_db
from frontend.routes import web_router

STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema is created on startup."""
    init_db()
    yield


app = FastAPI(
    title="Online Quiz System — Web Platform",
    description="Unified Web Application for Online Quiz Assessment",
    version="2.0.0",
    lifespan=lifespan,
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Register REST API routes
app.include_router(auth.router)
app.include_router(quizzes.router)
app.include_router(questions.router)
app.include_router(sessions.router)

# Register SSR Web Page routes
app.include_router(web_router)


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Online Quiz System Unified Web Platform",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
