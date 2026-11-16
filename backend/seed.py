"""
Seed script to populate initial sample data for demonstration and interactive testing.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from backend.database import SessionLocal, init_db
from backend.db_models import User, Quiz, Question, Session
from backend.services.auth_service import hash_password


def seed():
    init_db()
    db = SessionLocal()
    try:
        # 1. Create Demo Teacher if not exists
        teacher = db.query(User).filter(User.email == "teacher@university.edu").first()
        if not teacher:
            teacher = User(
                email="teacher@university.edu",
                password_hash=hash_password("password123"),
                name="Prof. Alex Smith",
                role="teacher",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            db.add(teacher)
            db.commit()
            db.refresh(teacher)
            print("Created teacher: teacher@university.edu / password123")
        else:
            teacher.name = "Prof. Alex Smith"
            db.commit()
            print("Teacher updated to generic name.")

        # 2. Create Demo Quiz if not exists
        quiz = db.query(Quiz).filter(Quiz.title == "TQM Quality Fundamentals Midterm").first()
        now = datetime.now(timezone.utc).isoformat()
        if not quiz:
            quiz = Quiz(
                title="TQM Quality Fundamentals Midterm",
                description="Assessment on Total Quality Management, continuous improvement, and quality engineering.",
                created_at=now,
                updated_at=now,
            )
            db.add(quiz)
            db.commit()
            db.refresh(quiz)

            # Add Questions
            q1 = Question(
                quiz_id=quiz.id,
                question_text="What does TQM stand for?",
                question_type="mcq",
                options_json=json.dumps([
                    "Total Quality Management",
                    "Technical Quantity Measurement",
                    "Team Quality Matrix",
                    "Total Quantity Method",
                ]),
                correct_answer="Total Quality Management",
                points=1,
                order_index=1,
                created_at=now,
            )
            q2 = Question(
                quiz_id=quiz.id,
                question_text="Relational database unique constraints eliminate duplicate records at the storage level.",
                question_type="true_false",
                options_json=json.dumps(["True", "False"]),
                correct_answer="True",
                points=1,
                order_index=2,
                created_at=now,
            )
            q3 = Question(
                quiz_id=quiz.id,
                question_text="Which country originated the Kaizen continuous improvement philosophy?",
                question_type="short_answer",
                options_json=None,
                correct_answer="Japan",
                points=2,
                order_index=3,
                created_at=now,
            )
            db.add_all([q1, q2, q3])
            db.commit()
            print("Created sample quiz with 3 questions.")

            # Create an active demo session
            demo_session = Session(
                quiz_id=quiz.id,
                session_code="TQM101",
                status="active",
                started_at=now,
            )
            db.add(demo_session)
            db.commit()
            print("Created active session: Code 'TQM101'")
        else:
            quiz.description = "Assessment on Total Quality Management, continuous improvement, and quality engineering."
            # Update q2 text if present
            q2 = db.query(Question).filter(Question.quiz_id == quiz.id, Question.order_index == 2).first()
            if q2:
                q2.question_text = "Relational database unique constraints eliminate duplicate records at the storage level."
            db.commit()
            print("Quiz and questions updated.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
