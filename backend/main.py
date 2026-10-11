"""
FastAPI application entry point for Online Quiz System.

Configures:
- Lifespan database initialization
- CORS middleware
- Route registration for Quizzes and Questions
- OpenAPI / Swagger documentation
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import questions, quizzes
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database schema is created on startup."""
    init_db()
    yield


app = FastAPI(
    title="Online Quiz System API",
    description="Backend API with Q06 Duplicate Entry Reduction for BBAT104 TQM Course Project",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for desktop clients and web frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(quizzes.router)
app.include_router(questions.router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Online Quiz System Backend",
        "quality_goal": "Q06: Reduce Duplicate Entries",
        "documentation": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
