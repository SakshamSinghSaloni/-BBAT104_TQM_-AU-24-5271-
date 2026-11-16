# System Architecture

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries  
**Version:** 2.0 | **Date:** 2026-11-16  
**Stack:** FastAPI + Jinja2 Web Server | SQLAlchemy 2.0 ORM | PostgreSQL / SQLite  

---

## 1. Architecture Overview

The Online Quiz System is built as a **unified server-rendered web application** with an integrated REST API. It eliminates external desktop dependencies, enabling instructors and students to interact seamlessly via standard web browsers.

```mermaid
flowchart TD
    subgraph Clients["Web Clients (Browser)"]
        TC["🧑‍🏫 Instructor\n(/dashboard, /quizzes, /sessions)"]
        SC["🧑‍🎓 Student\n(/join, /session/{code}/take)"]
    end

    subgraph AppServer["Unified Application Server (FastAPI + Uvicorn)"]
        direction TB
        ROUTER["Router & Web Pages Layer\n(FastAPI + Jinja2 Templates)"]
        MW["Security & Session Middleware\n(itsdangerous, bcrypt)"]
        SVC["Service Layer\n(QuizService, QuestionService,\nSessionService, GradingService)"]
        REPO["Repository Layer\n(SQLAlchemy 2.0 ORM)"]
    end

    subgraph Persistence["Persistence & Relational Integrity"]
        DB[("Database Engine\nPostgreSQL (Production)\nSQLite (Dev/Test)")]
        ALEMBIC["Alembic Migration Engine\n(Versioned DDL)"]
    end

    TC -->|"HTTP / HTTPS\n(Session Cookie)"| ROUTER
    SC -->|"HTTP / HTTPS\n(Ephemeral Session Code)"| ROUTER

    ROUTER --> MW
    MW --> SVC
    SVC --> REPO
    REPO --> DB
    ALEMBIC -.->|"Auto-migrations"| DB

    style TC fill:#2563eb,color:#fff
    style SC fill:#16a34a,color:#fff
    style ROUTER fill:#0284c7,color:#fff
    style MW fill:#d97706,color:#fff
    style SVC fill:#9333ea,color:#fff
    style REPO fill:#dc2626,color:#fff
    style DB fill:#475569,color:#fff
```

---

## 2. Layered Component Architecture

### 2.1 Web Presentation & Routing Layer (`frontend/`)
- **Jinja2 Server-Side Templates (`frontend/templates/`):**
  - Modular templates with base layout (`base.html`), navigation, flash notifications (`_flash.html`), and modal components.
  - Dedicated views for Instructor Dashboard, Quiz Library, Question Editor, and Live Analytics.
  - Dedicated student workflows for Session Entry (`/join`), Assessment Taking (`/session/{code}/take`), and Graded Results (`/session/{code}/results`).
- **Static Assets (`frontend/static/`):**
  - Responsive modern CSS (`style.css`) with CSS custom properties.
  - JavaScript client runtime (`app.js`) handling Q06 Poka-Yoke confirmation dialogs, double-click submission prevention, and dynamic question option controls.

### 2.2 Security & Authentication Layer (`backend/middleware/auth.py`)
- **Hybrid Security Model:**
  - Instructors authenticate via email and bcrypt-hashed password; identity is preserved via tamper-proof signed session cookies (`itsdangerous.URLSafeTimedSerializer`).
  - Students enter sessions ephemerally using their Student Identifier (Roll Number) and a 6-character session code; validated against duplicate entry constraints without account friction.

### 2.3 Domain Service Layer (`backend/services/`)
- **`QuizService`:** Handles quiz business logic, whitespace sanitization, and Search-Before-Add validation.
- **`QuestionService`:** Manages questions, options JSON serialization, and unique question prompts within a quiz.
- **`SessionService`:** Governs session lifecycle, collision-free code generation, student join validations, answer processing, and aggregated score analytics.
- **`GradingService`:** Deterministic auto-grading supporting MCQ exact matches, case-insensitive and whitespace-trimmed true/false and short answer evaluations.

### 2.4 Data Access & Persistence Layer (`backend/repositories/` & `backend/database.py`)
- **SQLAlchemy 2.0 ORM:** Modern declarative models (`backend/db_models.py`) with explicit foreign key cascading (`ondelete="CASCADE"`) and session boundaries.
- **Engine Interoperability:** Automatically operates on PostgreSQL in production via `psycopg2-binary` or SQLite in local test environments with `PRAGMA foreign_keys = ON` connection listeners.
- **Alembic:** Reversible, versioned database schema migration scripts (`alembic/versions/`).

---

## 3. Data Flow Diagrams

### 3.1 Quiz Creation Flow (Q06 Protected)

```mermaid
sequenceDiagram
    participant T as Instructor (Web)
    participant R as Router (/quizzes)
    participant S as QuizService
    participant Rep as QuizRepository
    participant D as Database

    T->>R: POST /quizzes {title, description}
    R->>S: create_quiz(QuizCreate)
    S->>S: Pre-Add Validation (Trim whitespace, check non-empty)
    S->>Rep: find_by_title(title)
    Rep->>D: SELECT WHERE title = :title
    alt Title Exists (Search Before Add)
        D-->>Rep: Found record
        Rep-->>S: Record
        S-->>R: HTTP 409 Conflict
        R-->>T: Re-render with Error Banner
    else Title Unique
        D-->>Rep: None
        S->>Rep: create(title, description)
        Rep->>D: INSERT INTO quizzes
        D-->>Rep: Success
        Rep-->>S: Quiz entity
        S-->>R: 201 Created / Redirect
        R-->>T: 303 Redirect to /quizzes
    end
```

### 3.2 Student Session Entry Flow (Q06 Protected)

```mermaid
sequenceDiagram
    participant St as Student (Web)
    participant R as Router (/join)
    participant S as SessionService
    participant Rep as SessionRepository
    participant D as Database

    St->>R: POST /join {session_code, name, student_id}
    R->>S: join_session(code, name, student_id)
    S->>Rep: get_session_by_code(code)
    alt Session Inactive / Missing
        S-->>R: HTTP 400 Bad Request
        R-->>St: Flash "Session not active"
    else Session Active
        S->>Rep: get_participant(session_id, student_id)
        alt Roll Number Already Joined (Search Before Add)
            Rep-->>S: Found participant
            S-->>R: HTTP 409 Conflict
            R-->>St: Flash "Roll Number already joined"
        else New Participant
            S->>Rep: create_participant(session_id, name, student_id)
            Rep->>D: INSERT INTO participants (UNIQUE checked)
            D-->>Rep: Success
            Rep-->>S: Participant record
            S-->>R: Redirect URL
            R-->>St: 303 Redirect to /session/{code}/take
        end
    end
```

---

## 4. Q06 Anti-Duplicate Defense Traceability

| Tier | Quality Defense Layer | Architectural Implementation |
|------|-----------------------|------------------------------|
| **Tier 1 (Storage)** | Relational Integrity | Unique constraints `ix_quizzes_title`, `ix_users_email`, `ix_sessions_session_code`, `uq_quiz_question_text`, `uq_session_participant`, `uq_participant_question`. |
| **Tier 2 (Pre-Add)** | Input Sanitization | Pydantic model validators + HTML5 input attributes strip whitespace and enforce bounds. |
| **Tier 3 (Service)** | Search-Before-Add | Explicit pre-insert query checks in `AuthService`, `QuizService`, and `SessionService` returning HTTP 409 early. |
| **Tier 4 (Poka-Yoke)** | User Interface Guard | Client-side modal dialogs (`_confirm_modal.html`) and rapid double-submit button disabling. |
