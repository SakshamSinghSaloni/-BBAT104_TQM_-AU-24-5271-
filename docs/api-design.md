# API Design Specification

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries  
**Version:** 2.0 | **Date:** 2026-11-16  
**Base URL:** `http://localhost:8000`  
**Authentication:** Signed HTTP-Only Session Cookie (`quiz_session`) via itsdangerous / FastAPI dependency  

---

## 1. Authentication Endpoints (`/api/auth`)

### POST /api/auth/register — Register Teacher
- **Purpose:** Create an instructor account.
- **Payload:** `{"name": "Prof. Smith", "email": "smith@univ.edu", "password": "securepassword"}`
- **Q06 Defense:** Pre-add validation checks non-empty name and email format; Search-Before-Add rejects duplicate email addresses (`409 Conflict`).
- **Response:** `201 Created` with User object + sets HTTP-only session cookie.

### POST /api/auth/login — Login Teacher
- **Purpose:** Authenticate teacher and establish session.
- **Payload:** `{"email": "smith@univ.edu", "password": "securepassword"}`
- **Response:** `200 OK` with User object + sets HTTP-only session cookie.
- **Error:** `401 Unauthorized` on invalid credentials.

### POST /api/auth/logout — Logout
- **Purpose:** Invalidate session.
- **Response:** `200 OK` + clears session cookie.

### GET /api/auth/me — Current User
- **Purpose:** Return current authenticated user profile.
- **Response:** `200 OK` with User object.

### PUT /api/auth/profile — Update Profile Name
- **Purpose:** Update authenticated instructor's display name.
- **Payload:** `{"name": "Prof. Alexander Bell"}`
- **Q06 Defense:** Tier 2 pre-add validator trims whitespace and rejects empty/blank strings (`422 Unprocessable Entity`).
- **Response:** `200 OK` with updated User object.
- **Errors:** `401 Unauthorized` if not authenticated; `422 Unprocessable Entity` if name is empty or exceeds 100 characters.

### PUT /api/auth/change-password — Change Password
- **Purpose:** Update authenticated instructor's password.
- **Payload:** `{"current_password": "oldPassword123", "new_password": "newSecurePassword456"}`
- **Security Defense:** Verifies existing credentials using bcrypt before updating; enforces $\ge 6$ character password length.
- **Response:** `200 OK` with `{"message": "Password changed successfully."}`.
- **Errors:** `401 Unauthorized` if current password is incorrect; `422 Unprocessable Entity` if new password is too short.

---

## 2. Quiz Endpoints (`/api/quizzes`)

### POST /api/quizzes — Create Quiz
- **Purpose:** Create a new quiz entity.
- **Payload:** `{"title": "TQM Fundamentals", "description": "Course Midterm"}`
- **Q06 Defense:** Rejects whitespace-only titles (`422`); rejects duplicate titles (`409 Conflict`).
- **Response:** `201 Created`

### GET /api/quizzes — List Quizzes
- **Purpose:** Retrieve all quizzes.
- **Response:** `200 OK` array of quizzes with `question_count`.

### GET /api/quizzes/{quiz_id} — Get Quiz Details
- **Response:** `200 OK` with quiz object. `404 Not Found` if missing.

### PUT /api/quizzes/{quiz_id} — Update Quiz
- **Payload:** `{"title": "Updated Title", "description": "Optional"}`
- **Q06 Defense:** Rejects duplicate titles (`409 Conflict`).

### DELETE /api/quizzes/{quiz_id} — Delete Quiz
- **Purpose:** Cascade deletes quiz, child questions, sessions, participants, and submissions.
- **Response:** `200 OK`

---

## 3. Question Endpoints (`/api/questions`)

### POST /api/quizzes/{quiz_id}/questions — Add Question
- **Payload:**
  ```json
  {
    "question_text": "What is the primary goal of Q06?",
    "question_type": "mcq",
    "options": ["Reduce Defective Code", "Reduce Duplicate Entries", "Speed Up UI"],
    "correct_answer": "Reduce Duplicate Entries",
    "points": 1,
    "order_index": 0
  }
  ```
- **Q06 Defense:** Pre-add validation checks MCQ options and inclusion of correct answer; Search-Before-Add rejects identical question prompts within the same quiz (`409 Conflict`).
- **Response:** `201 Created`

### GET /api/quizzes/{quiz_id}/questions — List Questions
- **Response:** `200 OK` array of questions.

### PUT /api/questions/{question_id} — Update Question
- **Response:** `200 OK` with updated question.

### DELETE /api/questions/{question_id} — Delete Question
- **Response:** `200 OK`

---

## 4. Session & Assessment Endpoints (`/api/sessions`)

### POST /api/sessions — Launch Session
- **Purpose:** Instructor starts a live assessment session.
- **Payload:** `{"quiz_id": 1}`
- **Response:** `201 Created` with generated 6-character collision-free `session_code` (e.g. `"7X3K9P"`).

### GET /api/sessions — List Sessions
- **Purpose:** List all active and past sessions.
- **Response:** `200 OK`

### POST /api/sessions/{session_id}/end — End Session
- **Purpose:** Close session to new joins and submissions.
- **Response:** `200 OK` with updated status `"ended"`.

### GET /api/sessions/{session_id}/results — Session Analytics
- **Purpose:** Aggregated analytics for instructors.
- **Response:** `200 OK` with `leaderboard`, `question_stats`, `average_score`, `highest_score`.

---

## 5. Student Ephemeral Endpoints

### POST /api/sessions/{session_code}/join — Join Session
- **Purpose:** Ephemeral student registration.
- **Payload:** `{"student_name": "Alex Morgan", "student_identifier": "STU-1001"}`
- **Q06 Defense:** Pre-add validation on non-empty values; Search-Before-Add rejects duplicate joins by the same Roll Number in this session (`409 Conflict`).
- **Response:** `201 Created` with `ParticipantResponse`.

### GET /api/sessions/{session_code}/questions — Fetch Questions
- **Purpose:** Retrieve test items for the active session. Omits `correct_answer` to preserve exam security.
- **Response:** `200 OK` array of questions.

### POST /api/sessions/{session_code}/submit — Submit Answers
- **Purpose:** Submit all answers for automated grading.
- **Payload:**
  ```json
  {
    "participant_id": 1,
    "answers": [
      {"question_id": 1, "answer_text": "Reduce Duplicate Entries"}
    ]
  }
  ```
- **Q06 Defense:** Search-Before-Add rejects duplicate quiz submissions from the same participant (`409 Conflict`).
- **Response:** `200 OK` with `StudentQuizResult` containing total score, max score, percentage, and detailed evaluations.

---

## 6. Living Documentation

Interactive API explorers are served directly from the running backend:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
