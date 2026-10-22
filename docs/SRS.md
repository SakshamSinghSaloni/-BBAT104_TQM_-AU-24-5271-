# Software Requirements Specification (SRS)

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries
**Course:** BBAT104 — Fundamentals of TQM
**Student:** Saksham Singh Saloni (AU-24-5271)
**Academic Session:** 2026–27
**Version:** 1.0
**Date:** 2026-10-11

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for the **Online Quiz System**, a desktop-based application that allows teachers to create and conduct quizzes, and students to participate and receive graded results. The system implements Quality Goal Q06 (Reduce Duplicate Entries) to ensure data integrity throughout all operations.

### 1.2 Scope

The Online Quiz System consists of:

- A **backend server** (FastAPI) that owns application logic, database access, validation, and grading.
- A **teacher desktop client** (PySide6) for quiz and question management, session control, and result viewing.
- A **student desktop client** (PySide6) for joining sessions, answering questions, and viewing results.

The system communicates over HTTP REST APIs, with the backend serving as the single point of data access. This architecture supports both local-network and eventual internet-based deployment.

### 1.3 Intended Users

| User Role | Description |
|-----------|-------------|
| **Teacher / Conductor** | Creates quizzes, manages questions, starts quiz sessions, monitors participation, views results. |
| **Student / Participant** | Joins active quiz sessions, answers questions, submits responses, views results when permitted. |

### 1.4 Definitions and Abbreviations

| Term | Definition |
|------|-----------|
| CRUD | Create, Read, Update, Delete operations |
| Q06 | Quality Goal 06 — Reduce Duplicate Entries |
| SRS | Software Requirements Specification |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| TQM | Total Quality Management |
| SQC | Statistical Quality Control |
| FMEA | Failure Mode and Effects Analysis |
| RPN | Risk Priority Number (Severity × Occurrence × Detection) |
| PDCA | Plan-Do-Check-Act cycle |
| SIPOC | Suppliers-Inputs-Process-Outputs-Customers |
| CTQ | Critical to Quality |

---

## 2. Overall System Description

### 2.1 System Architecture Overview

```
┌──────────────────┐     HTTP/REST     ┌──────────────────┐     SQL      ┌──────────┐
│  Teacher Client   │ ◄──────────────► │                  │ ◄──────────► │          │
│  (PySide6)        │                  │  Backend Server   │              │  SQLite   │
│                   │                  │  (FastAPI +        │              │  Database │
│                   │                  │   Uvicorn)         │              │          │
└──────────────────┘                  │                   │              └──────────┘
                                       │  - API Layer       │
┌──────────────────┐     HTTP/REST     │  - Service Layer   │
│  Student Client   │ ◄──────────────► │  - Repository Layer│
│  (PySide6)        │                  │                   │
└──────────────────┘                  └──────────────────┘
```

### 2.2 Key Design Principles

1. **Client-server separation:** Desktop clients never access the database directly.
2. **Server-side authority:** All validation, grading, and duplicate-prevention checks are enforced by the backend.
3. **Layered architecture:** API layer → Service layer → Repository layer → Database.
4. **Data integrity first:** Database constraints enforce uniqueness; application-layer checks provide better user feedback.

### 2.3 Constraints and Assumptions

- **C1:** Python 3.x runtime is available on the user's machine.
- **C2:** SQLite is used for initial development; PostgreSQL may be adopted for production deployment.
- **C3:** Internet deployment is a long-term goal; the immediate deliverable operates on localhost.
- **C4:** The system does not require exam-grade security (proctoring, tab-switching detection).
- **A1:** The teacher and student may be on the same network initially; internet communication is architecturally supported but not required for Reviews 1–2.
- **A2:** A single teacher operates one quiz session at a time in the initial version.

---

## 3. Functional Requirements

### 3.1 Quiz Management

| ID | Requirement | Priority | Review |
|----|------------|----------|--------|
| FR-01 | **Create a quiz:** The teacher can create a new quiz with a title and optional description. The backend validates required fields and checks for empty/blank inputs before insertion. | Must | R2 |
| FR-02 | **List quizzes:** The teacher can retrieve and view all existing quizzes with their titles, descriptions, question counts, and creation dates. | Must | R2 |
| FR-03 | **Update a quiz:** The teacher can modify the title and description of an existing quiz. The backend validates the updated data and returns a not-found error if the quiz does not exist. | Must | R2 |
| FR-04 | **Delete a quiz:** The teacher can delete a quiz. The system displays a confirmation dialog before proceeding. Deleting a quiz cascades to its questions and any associated sessions. | Must | R2 |

### 3.2 Question Management

| ID | Requirement | Priority | Review |
|----|------------|----------|--------|
| FR-05 | **Add a question:** The teacher can add a question to a quiz, specifying question text, question type (e.g., multiple-choice), options (for MCQ), correct answer, and points. The backend validates all required fields. | Must | R2 |
| FR-06 | **List questions:** The teacher can view all questions belonging to a specific quiz, including their text, type, options, and points. | Must | R2 |
| FR-07 | **Update a question:** The teacher can edit a question's text, options, correct answer, or points. The backend validates the updated data. | Must | R2 |
| FR-08 | **Delete a question:** The teacher can delete a question. The system displays a confirmation dialog before proceeding. | Must | R2 |

### 3.3 Quiz Session (stretch for Review 2, planned for future)

| ID | Requirement | Priority | Review |
|----|------------|----------|--------|
| FR-09 | **Start a session:** The teacher can start a quiz session, which generates a unique session code for students to join. | Should | R2+ |
| FR-10 | **Join a session:** A student can join an active session by entering the session code and their name/identifier. The backend prevents the same student from joining a session twice. | Should | R2+ |
| FR-11 | **Submit answers:** A student can submit answers to quiz questions. The backend prevents duplicate submissions for the same question by the same participant. | Should | R2+ |
| FR-12 | **Auto-grade:** The backend automatically grades supported question types (e.g., MCQ) by comparing submitted answers to correct answers. | Should | R2+ |
| FR-13 | **View results:** The teacher can view submission results and scores for a session. Students can view their own results when the session permits. | Could | Future |
| FR-14 | **Monitor progress:** The teacher can see which students have joined and their submission progress during an active session. | Could | Future |

### 3.4 Q06 — Reduce Duplicate Entries

| ID | Requirement | Q06 Feature | Priority | Review |
|----|------------|-------------|----------|--------|
| FR-Q1 | **Unique ID Constraints:** The database enforces uniqueness on primary keys, session codes, and composite keys (e.g., one submission per participant per question). Attempts to insert duplicate records produce clear errors rather than silent failures. | Unique ID Constraints | Must | R2 |
| FR-Q2 | **Pre-add Validation:** Before inserting any record, the backend validates all required fields are present, non-blank, and within acceptable ranges. Invalid data is rejected with descriptive error messages. | Pre-add Validation | Must | R2 |
| FR-Q3 | **Search Before Add:** Before creating a record, the service layer checks whether a matching record already exists (e.g., a student already registered in the session). The search criteria and duplicate definition are documented for each entity. | Search Before Add | Must | R2 |
| FR-Q4 | **Confirmation Dialogs:** The desktop client displays confirmation dialogs before destructive or consequential actions: deleting a quiz, deleting a question, and ending a session. Routine actions (creating, editing) do not require confirmation. | Confirmation Dialogs | Must | R2 |

> **Note:** The official Q06 feature matrix lists 4 features. The guidelines state "select and implement any 5 features." This discrepancy is recorded as an open question (see Section 8). The project implements all 4 listed features.

---

## 4. Non-Functional Requirements

| ID | Category | Requirement | Proposed Target |
|----|----------|------------|-----------------|
| NFR-01 | Maintainability | Code is organized into clearly separated layers (API, service, repository). Business logic does not reside in UI code. | Layered architecture maintained across all modules |
| NFR-02 | Usability | The teacher client provides clear feedback for all operations: success messages, validation errors, and not-found conditions. | Every CRUD operation produces visible feedback |
| NFR-03 | Data Integrity | Database constraints (primary keys, unique constraints, NOT NULL, foreign keys with CASCADE) prevent invalid or duplicate data at the storage level. | Zero orphaned or duplicate records in normal operation |
| NFR-04 | Testability | Core business logic and database constraints are covered by automated tests using pytest. | Tests for all CRUD success paths, invalid inputs, and duplicate scenarios |
| NFR-05 | Responsiveness | The backend responds to CRUD API requests within a reasonable timeframe under local operation. | < 500ms response time for CRUD operations on localhost |
| NFR-06 | Reliability | The system handles errors gracefully. Network failures, missing records, and invalid inputs produce informative errors rather than crashes. | No unhandled exceptions in normal user workflows |
| NFR-07 | Security | The backend validates all inputs server-side. No client-supplied grading results are trusted. Credentials and secrets are not hardcoded or committed. | Input validation on all endpoints; no secrets in repository |
| NFR-08 | Deployment Readiness | The architecture supports transition from localhost to internet deployment without major redesign. | Backend accessible via HTTP; no direct DB file sharing |

---

## 5. External Interface Requirements

### 5.1 User Interfaces

- **Teacher Client:** PySide6 desktop application with views for quiz management, question management, and (future) session management.
- **Student Client:** PySide6 desktop application with views for joining sessions, answering questions, and viewing results.

### 5.2 Software Interfaces

- **Backend API:** RESTful HTTP API served by FastAPI on a configurable host and port.
- **Database:** SQLite3 database file accessed exclusively by the backend process.
- **HTTP Client:** Desktop clients use `httpx` to communicate with the backend.

### 5.3 Communication Interfaces

- **HTTP REST:** Used for all CRUD operations, session management, and submissions.
- **WebSocket (planned):** Intended for real-time progress updates from backend to teacher client. Not implemented in the initial version.

---

## 6. Data Requirements

### 6.1 Entities

| Entity | Description | Key Fields |
|--------|------------|------------|
| Quiz | A collection of questions created by a teacher | id (PK), title, description, created_at, updated_at |
| Question | A single question within a quiz | id (PK), quiz_id (FK), question_text, question_type, options_json, correct_answer, points, order_index |
| Session | An active instance of a quiz for student participation | id (PK), quiz_id (FK), session_code (UNIQUE), status, started_at, ended_at |
| Participant | A student who has joined a session | id (PK), session_id (FK), student_name, student_identifier, joined_at |
| Submission | A student's answer to a question | id (PK), participant_id (FK), question_id (FK), answer_text, is_correct, points_awarded, submitted_at |

### 6.2 Key Constraints

| Constraint | Table | Type | Purpose |
|-----------|-------|------|---------|
| Primary key auto-increment | All tables | PK | Unique record identification |
| quiz_id FK → Quiz.id | Question | FK CASCADE | Questions belong to a quiz; cascade on delete |
| quiz_id FK → Quiz.id | Session | FK CASCADE | Sessions reference a quiz |
| session_id FK → Session.id | Participant | FK CASCADE | Participants belong to a session |
| UNIQUE(session_code) | Session | UNIQUE | Prevent duplicate session codes |
| UNIQUE(session_id, student_identifier) | Participant | UNIQUE | Prevent same student joining a session twice |
| UNIQUE(participant_id, question_id) | Submission | UNIQUE | Prevent duplicate answer submissions |
| NOT NULL on required fields | All tables | NOT NULL | Prevent missing required data |

---

## 7. Acceptance Criteria

### 7.1 CRUD Operations

| Scenario | Expected Behaviour |
|----------|-------------------|
| Create a quiz with valid title and description | Quiz is created; returned with assigned ID and timestamps |
| Create a quiz with blank title | Request rejected with validation error; no record created |
| List quizzes when several exist | All quizzes returned with correct data |
| List quizzes when none exist | Empty list returned (not an error) |
| Update an existing quiz | Quiz fields are updated; updated_at reflects the change |
| Update a non-existent quiz | 404 Not Found error returned |
| Delete a quiz (confirmed) | Quiz and its questions are deleted; confirmation dialog shown first |
| Delete a quiz (cancelled) | No deletion occurs |
| Create a question with valid data | Question added to the quiz |
| Create a question with missing required fields | Validation error returned |

### 7.2 Q06 — Duplicate Entry Reduction

| Scenario | Expected Behaviour | Q06 Feature |
|----------|-------------------|-------------|
| Insert a record with a duplicate unique key | Database rejects the insert; clear error message returned | Unique ID Constraints |
| Submit a quiz creation request with blank title | Rejected before reaching the database; descriptive error | Pre-add Validation |
| Attempt to add a student who already exists in a session | Service layer detects the duplicate via search; returns a specific "already exists" error | Search Before Add |
| Teacher clicks "Delete Quiz" | Confirmation dialog appears asking "Are you sure?"; deletion proceeds only if confirmed | Confirmation Dialogs |
| Teacher clicks "Delete Question" | Same confirmation dialog behaviour | Confirmation Dialogs |

---

## 8. Open Questions

| # | Question | Status |
|---|----------|--------|
| OQ-1 | The guidelines require 5 Q06 features, but the Q06 row lists only 4. Should a 5th feature be proposed, or is implementing all 4 listed features sufficient? | **Pending professor clarification** |
| OQ-2 | Should student authentication use a simple name/identifier, or is a login system required for Reviews 1–2? | Deferred; simple identifier used initially |
| OQ-3 | Should the teacher be able to run multiple concurrent sessions? | Deferred; single session per teacher initially |

---

## 9. Requirements Traceability

| Requirement | Module | Test / Evidence | Status |
|-------------|--------|----------------|--------|
| FR-01 Create quiz | `backend/api/quizzes.py`, `backend/services/quiz_service.py` | `tests/test_api.py::test_api_create_quiz_success` | ✅ Implemented & Tested |
| FR-02 List quizzes | `backend/api/quizzes.py` | `tests/test_api.py::test_api_list_quizzes` | ✅ Implemented & Tested |
| FR-03 Update quiz | `backend/api/quizzes.py` | `tests/test_api.py::test_api_update_quiz` | ✅ Implemented & Tested |
| FR-04 Delete quiz | `backend/api/quizzes.py`, `apps/teacher/views/quiz_view.py` | `tests/test_api.py::test_api_delete_quiz` | ✅ Implemented & Tested |
| FR-05 Add question | `backend/api/questions.py`, `backend/services/question_service.py` | `tests/test_api.py::test_api_add_and_list_question` | ✅ Implemented & Tested |
| FR-06 List questions | `backend/api/questions.py` | `tests/test_api.py::test_api_add_and_list_question` | ✅ Implemented & Tested |
| FR-07 Update question | `backend/api/questions.py` | `tests/test_api.py::test_api_update_question` | ✅ Implemented & Tested |
| FR-08 Delete question | `backend/api/questions.py`, `apps/teacher/views/question_view.py` | `tests/test_api.py::test_api_delete_question` | ✅ Implemented & Tested |
| FR-Q1 Unique ID Constraints | `backend/database.py` | `tests/test_database.py` (all tests) | ✅ Implemented & Tested |
| FR-Q2 Pre-add Validation | `backend/models.py`, `backend/services/*` | `tests/test_services.py`, `tests/test_api.py` | ✅ Implemented & Tested |
| FR-Q3 Search Before Add | `backend/services/*`, `backend/repositories/*` | `tests/test_services.py` | ✅ Implemented & Tested |
| FR-Q4 Confirmation Dialogs | `apps/teacher/views/*` | `apps/teacher/views/quiz_view.py`, `question_view.py` | ✅ Implemented & Verified |
| FR-09 to FR-14 Quiz Session Flow | `backend/api/`, `apps/student/` | Automated test suite (planned) | 🔲 Planned (Stretch) |
