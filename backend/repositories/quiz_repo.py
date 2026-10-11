"""
Data access repository for Quiz entities.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class QuizRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        now = datetime.now().isoformat()
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO quizzes (title, description, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, now, now),
        )
        self.conn.commit()
        return self.get_by_id(cursor.lastrowid)  # type: ignore

    def get_by_id(self, quiz_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT q.id, q.title, q.description, q.created_at, q.updated_at,
                   (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) AS question_count
            FROM quizzes q
            WHERE q.id = ?
            """,
            (quiz_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)

    def list_all(self) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT q.id, q.title, q.description, q.created_at, q.updated_at,
                   (SELECT COUNT(*) FROM questions WHERE quiz_id = q.id) AS question_count
            FROM quizzes q
            ORDER BY q.id DESC
            """
        )
        return [dict(row) for row in cursor.fetchall()]

    def find_by_title(self, title: str) -> List[Dict[str, Any]]:
        """Used for Q06 Feature 3: Search Before Add."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, title, description, created_at, updated_at
            FROM quizzes
            WHERE LOWER(title) = LOWER(?)
            """,
            (title.strip(),),
        )
        return [dict(row) for row in cursor.fetchall()]

    def update(self, quiz_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        existing = self.get_by_id(quiz_id)
        if not existing:
            return None

        new_title = title if title is not None else existing["title"]
        new_desc = description if description is not None else existing["description"]
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE quizzes
            SET title = ?, description = ?, updated_at = ?
            WHERE id = ?
            """,
            (new_title, new_desc, now, quiz_id),
        )
        self.conn.commit()
        return self.get_by_id(quiz_id)

    def delete(self, quiz_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        self.conn.commit()
        return cursor.rowcount > 0
