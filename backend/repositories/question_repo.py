"""
Data access repository for Question entities.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class QuestionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(
        self,
        quiz_id: int,
        question_text: str,
        question_type: str,
        options: Optional[List[str]],
        correct_answer: str,
        points: int = 1,
        order_index: int = 0,
    ) -> Dict[str, Any]:
        options_json = json.dumps(options) if options is not None else None
        now = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO questions (
                quiz_id, question_text, question_type, options_json,
                correct_answer, points, order_index, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                quiz_id,
                question_text,
                question_type,
                options_json,
                correct_answer,
                points,
                order_index,
                now,
            ),
        )
        self.conn.commit()
        return self.get_by_id(cursor.lastrowid)  # type: ignore

    def get_by_id(self, question_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, quiz_id, question_text, question_type, options_json,
                   correct_answer, points, order_index, created_at
            FROM questions
            WHERE id = ?
            """,
            (question_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None

        data = dict(row)
        data["options"] = json.loads(data.pop("options_json")) if data.get("options_json") else None
        return data

    def list_by_quiz(self, quiz_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, quiz_id, question_text, question_type, options_json,
                   correct_answer, points, order_index, created_at
            FROM questions
            WHERE quiz_id = ?
            ORDER BY order_index ASC, id ASC
            """,
            (quiz_id,),
        )
        questions = []
        for row in cursor.fetchall():
            data = dict(row)
            data["options"] = json.loads(data.pop("options_json")) if data.get("options_json") else None
            questions.append(data)
        return questions

    def find_duplicate_in_quiz(self, quiz_id: int, question_text: str) -> List[Dict[str, Any]]:
        """Used for Q06 Feature 3: Search Before Add."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, quiz_id, question_text
            FROM questions
            WHERE quiz_id = ? AND LOWER(TRIM(question_text)) = LOWER(TRIM(?))
            """,
            (quiz_id, question_text),
        )
        return [dict(row) for row in cursor.fetchall()]

    def update(
        self,
        question_id: int,
        question_text: Optional[str] = None,
        options: Optional[List[str]] = None,
        correct_answer: Optional[str] = None,
        points: Optional[int] = None,
        order_index: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        existing = self.get_by_id(question_id)
        if not existing:
            return None

        new_text = question_text if question_text is not None else existing["question_text"]
        new_opts = options if options is not None else existing["options"]
        new_opts_json = json.dumps(new_opts) if new_opts is not None else None
        new_ans = correct_answer if correct_answer is not None else existing["correct_answer"]
        new_pts = points if points is not None else existing["points"]
        new_idx = order_index if order_index is not None else existing["order_index"]

        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE questions
            SET question_text = ?, options_json = ?, correct_answer = ?,
                points = ?, order_index = ?
            WHERE id = ?
            """,
            (new_text, new_opts_json, new_ans, new_pts, new_idx, question_id),
        )
        self.conn.commit()
        return self.get_by_id(question_id)

    def delete(self, question_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        self.conn.commit()
        return cursor.rowcount > 0
