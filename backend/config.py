"""
Centralized application configuration.
Supports environment-based configuration via python-dotenv.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the backend
BASE_DIR = Path(__file__).resolve().parent

# Load .env from project root if present
ENV_PATH = BASE_DIR.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Database Configuration
# Default: SQLite file for local development/testing; Override via DATABASE_URL for PostgreSQL
DEFAULT_SQLITE_PATH = BASE_DIR / "quiz_system.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"

DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# Authentication & Security
SECRET_KEY: str = os.getenv("SECRET_KEY", "tqm-quiz-system-super-secret-key-change-in-production")
ALGORITHM: str = "HS256"
SESSION_COOKIE_NAME: str = "quiz_session"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
