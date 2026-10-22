# API Design

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries
**Version:** 1.0 | **Date:** 2026-10-11
**Base URL:** `http://localhost:8000`

---

## 1. Quiz Endpoints

### POST /api/quizzes — Create a quiz

- **Purpose:** Create a new quiz record.
- **Request body:**
  ```json
  {
    "title": "Python Basics Quiz",
    "description": "A quiz covering fundamental Python concepts"
  }
  ```
- **Validation (Q06: Pre-add Validation):**
  - `title` is required and must not be blank or whitespace-only.
  - `title` max length: 200 characters.
  - `description` is optional; max length: 1000 characters.
- **Duplicate check (Q06: Search Before Add):**
  - Strict: checks if a quiz with identical title already exists (case-insensitive). Blocks creation and returns 409 Conflict.
- **Success response:** `201 Created`
  ```json
  {
    "id": 1,
    "title": "Python Basics Quiz",
    "description": "A quiz covering fundamental Python concepts",
    "question_count": 0,
    "created_at": "2026-10-11T18:00:00",
    "updated_at": "2026-10-11T18:00:00"
  }
  ```
- **Error responses:**
  - `409 Conflict` — duplicate quiz title detected (Q06: Search Before Add).
  - `422 Unprocessable Entity` — validation failure (missing/blank title).

---

### GET /api/quizzes — List all quizzes

- **Purpose:** Retrieve all quizzes.
- **Response:** `200 OK`
  ```json
  [
    {
      "id": 1,
      "title": "Python Basics Quiz",
      "description": "...",
      "question_count": 5,
      "created_at": "2026-10-11T18:00:00",
      "updated_at": "2026-10-11T18:00:00"
    }
  ]
  ```
- Returns an empty array `[]` if no quizzes exist.

---

### GET /api/quizzes/{quiz_id} — Get quiz details

- **Purpose:** Retrieve a single quiz by ID.
- **Response:** `200 OK` with quiz object.
- **Error:** `404 Not Found` if quiz does not exist.

---

### PUT /api/quizzes/{quiz_id} — Update a quiz

- **Purpose:** Update title and/or description of an existing quiz.
- **Request body:**
  ```json
  {
    "title": "Updated Title",
    "description": "Updated description"
  }
  ```
- **Validation:** Same as creation.
- **Response:** `200 OK` with updated quiz object.
- **Errors:**
  - `404 Not Found` — quiz does not exist.
  - `409 Conflict` — new title duplicates an existing quiz title (Q06: Search Before Add).
  - `422 Unprocessable Entity` — validation failure.

---

### DELETE /api/quizzes/{quiz_id} — Delete a quiz

- **Purpose:** Delete a quiz and cascade to its questions and sessions.
- **Note:** The desktop client shows a confirmation dialog before calling this endpoint (Q06: Confirmation Dialogs).
- **Response:** `200 OK`
  ```json
  { "message": "Quiz deleted successfully" }
  ```
- **Error:** `404 Not Found` — quiz does not exist.

---

## 2. Question Endpoints

### POST /api/quizzes/{quiz_id}/questions — Add a question

- **Purpose:** Add a question to a specific quiz.
- **Request body:**
  ```json
  {
    "question_text": "What is the output of print(2 + 3)?",
    "question_type": "mcq",
    "options": ["3", "5", "23", "Error"],
    "correct_answer": "5",
    "points": 2
  }
  ```
- **Validation (Q06: Pre-add Validation):**
  - `question_text` is required, non-blank, max 2000 characters.
  - `question_type` must be one of: `mcq`, `true_false`, `short_answer`.
  - For `mcq`: `options` must be a non-empty list of 2–6 options.
  - `correct_answer` is required and must be non-blank.
  - For `mcq`: `correct_answer` must match one of the `options`.
  - `points` must be a positive integer (default: 1).
- **Duplicate check (Q06: Search Before Add):**
  - Strict: checks if a question with identical `question_text` already exists in the same quiz. Blocks creation and returns 409 Conflict.
- **Response:** `201 Created` with question object.
- **Errors:**
  - `404 Not Found` — parent quiz does not exist.
  - `409 Conflict` — duplicate question in quiz (Q06: Search Before Add).
  - `422 Unprocessable Entity` — validation failure.

---

### GET /api/quizzes/{quiz_id}/questions — List questions for a quiz

- **Response:** `200 OK` with array of question objects (ordered by `order_index`).
- **Error:** `404 Not Found` — quiz does not exist.

---

### GET /api/questions/{question_id} — Get question details

- **Response:** `200 OK` with question object.
- **Error:** `404 Not Found`.

---

### PUT /api/questions/{question_id} — Update a question

- **Request body:** Same fields as creation (all optional for partial update).
- **Validation:** Same rules as creation for provided fields.
- **Response:** `200 OK` with updated question.
- **Errors:**
  - `404 Not Found` — question does not exist.
  - `409 Conflict` — updated text duplicates another question in the quiz or answer not in options (Q06: Search Before Add / Pre-add Validation).
  - `422 Unprocessable Entity` — invalid data formats.

---

### DELETE /api/questions/{question_id} — Delete a question

- **Note:** Confirmation dialog shown by client before calling.
- **Response:** `200 OK` with success message.
- **Error:** `404 Not Found`.

---

## 3. Session Endpoints (Planned — Stretch for Review 2)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/api/sessions` | Start a new quiz session |
| POST | `/api/sessions/{code}/join` | Student joins a session |
| POST | `/api/sessions/{session_id}/submit` | Submit answers |
| PATCH | `/api/sessions/{session_id}/end` | End a session |
| GET | `/api/sessions/{session_id}/results` | View results |
| GET | `/api/sessions/{session_id}/participants` | List participants |

These endpoints are documented but implementation is deferred to stretch/future scope.

---

## 4. Common Error Response Format

All error responses follow a consistent shape:

```json
{
  "detail": "Quiz not found"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

---

## 5. Auto-generated API Documentation

FastAPI provides interactive documentation at:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

These are available automatically when the backend is running and serve as live API reference during development.
