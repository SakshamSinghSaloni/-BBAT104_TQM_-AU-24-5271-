"""
HTTP Client wrapping backend REST API calls for the Teacher Desktop Application.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx


class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    # ==========================
    # QUIZ API CALLS
    # ==========================

    def create_quiz(self, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.post("/api/quizzes", json={"title": title, "description": description})
            resp.raise_for_status()
            return resp.json()

    def list_quizzes(self) -> List[Dict[str, Any]]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.get("/api/quizzes")
            resp.raise_for_status()
            return resp.json()

    def get_quiz(self, quiz_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.get(f"/api/quizzes/{quiz_id}")
            resp.raise_for_status()
            return resp.json()

    def update_quiz(self, quiz_id: int, title: str, description: Optional[str] = None) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.put(f"/api/quizzes/{quiz_id}", json={"title": title, "description": description})
            resp.raise_for_status()
            return resp.json()

    def delete_quiz(self, quiz_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.delete(f"/api/quizzes/{quiz_id}")
            resp.raise_for_status()
            return resp.json()

    # ==========================
    # QUESTION API CALLS
    # ==========================

    def add_question(
        self,
        quiz_id: int,
        question_text: str,
        question_type: str,
        options: Optional[List[str]],
        correct_answer: str,
        points: int = 1,
    ) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.post(
                f"/api/quizzes/{quiz_id}/questions",
                json={
                    "question_text": question_text,
                    "question_type": question_type,
                    "options": options,
                    "correct_answer": correct_answer,
                    "points": points,
                },
            )
            resp.raise_for_status()
            return resp.json()

    def list_questions(self, quiz_id: int) -> List[Dict[str, Any]]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.get(f"/api/quizzes/{quiz_id}/questions")
            resp.raise_for_status()
            return resp.json()

    def delete_question(self, question_id: int) -> Dict[str, Any]:
        with httpx.Client(base_url=self.base_url, timeout=5.0) as client:
            resp = client.delete(f"/api/questions/{question_id}")
            resp.raise_for_status()
            return resp.json()
