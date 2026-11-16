"""
Repository for User persistence using SQLAlchemy 2.0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db_models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, email: str, password_hash: str, name: str, role: str = "teacher") -> User:
        now = datetime.now(timezone.utc).isoformat()
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            name=name.strip(),
            role=role.strip().lower(),
            created_at=now,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self) -> list[User]:
        stmt = select(User).order_by(User.id.asc())
        return list(self.db.execute(stmt).scalars().all())
