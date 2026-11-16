# ADR-002: Production Database Engine Upgrade to SQLAlchemy 2.0 and Alembic

**Date:** 2026-11-16  
**Status:** Accepted  
**Supercedes:** Partially supersedes the Database selection in ADR-001  

## Context

In the initial prototype (ADR-001), raw SQLite3 via Python's standard `sqlite3` driver was used. While sufficient for single-threaded standalone demos, several architectural and production requirements emerged as part of the TQM Quality Goal Q06 (Reduce Duplicate Entries) and the transition to a unified multi-user web application:
1. **Concurrent Write Collisions:** SQLite operates with coarse database-level file locks (`database is locked` errors during simultaneous student joins or submissions). A production-grade multi-user classroom environment demands row-level locking and connection pooling.
2. **Multi-Database Portability:** The system must run smoothly in local student development environments (SQLite without external daemon dependencies) while deploying seamlessly to PostgreSQL in production.
3. **Database Migrations:** Modifying schemas, adding indices, and evolving constraints (such as `uq_quiz_question_text` and `uq_session_participant`) across environments requires automated, versioned DDL migration scripts rather than manual SQLite table re-creation.
4. **User & Identity Schema:** Supporting teacher authentication and authorization requires a secure, relational `users` table linked to quizzes and sessions.

## Decision

We upgrade the persistence layer from raw `sqlite3` to **SQLAlchemy 2.0 ORM** with **Alembic** migrations and **psycopg2-binary** / SQLite driver interoperability:

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **ORM / Core Engine** | **SQLAlchemy 2.0+** | Modern typed declarative ORM with strict session boundaries, connection pooling (`QueuePool` / `NullPool`), and standard SQL 2.0 `select()` syntax. |
| **Migrations** | **Alembic** | Automated migration generation (`revision --autogenerate`), batch-mode SQLite migration compatibility (`render_as_batch=True`), and reproducible schema history. |
| **Database Drivers** | `psycopg2-binary` (PostgreSQL) + `sqlite3` (Fallback/Test) | Production PostgreSQL capability with zero-setup SQLite fallback via `DATABASE_URL`. |
| **Configuration** | `backend/config.py` + `python-dotenv` | Centralized twelve-factor app configuration via `.env` files. |
| **SQLite Safety** | Event listener `PRAGMA foreign_keys=ON` | Ensures SQLite strictly enforces foreign key cascades and integrity identical to PostgreSQL. |

## Schema Enhancements for Q06

The SQLAlchemy declarative models (`backend/db_models.py`) explicitly encode the multi-tier Q06 defense directly in the database engine:
- `users`: Teacher/admin authentication with unique index on `email`.
- `quizzes`: Unique index on `title` (`ix_quizzes_title`).
- `questions`: Composite unique constraint `UniqueConstraint('quiz_id', 'question_text', name='uq_quiz_question_text')`.
- `sessions`: Unique index on `session_code` (`ix_sessions_session_code`).
- `participants`: Composite unique constraint `UniqueConstraint('session_id', 'student_identifier', name='uq_session_participant')` preventing duplicate participant entries in a session.
- `submissions`: Composite unique constraint `UniqueConstraint('participant_id', 'question_id', name='uq_participant_question')` preventing duplicate submissions for a given question.
- All foreign keys specify `ondelete="CASCADE"` to ensure strict relational integrity upon deletion of parent entities.

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| **Direct Raw SQL with PostgreSQL driver** | High boilerplate; manual SQL strings across repositories; lacks automated schema migration tracking and cross-engine portability. |
| **Tortoise ORM / Gino (Async ORM)** | Adds excessive async complexity to relational domain logic without tangible throughput benefit for standard classroom quiz workloads. |
| **Django ORM** | Requires adopting the entire Django monolithic web framework, which contradicts the lightweight FastAPI micro-framework design. |

## Consequences

- **Positive:**
  - Full PostgreSQL compatibility with connection pooling in production deployments.
  - Zero-configuration SQLite developer/test workflow using `sqlite:///./backend/quiz_system.db`.
  - Schema migrations are automated and tracked under version control in `alembic/versions/`.
  - Elimination of raw cursor leaks and manual dictionary-mapping boilerplate.
  - Repository layer interacts cleanly with `Session` instances, injectable via FastAPI's `Depends(get_db)`.
- **Negative / Trade-offs:**
  - Additional dependencies in `requirements.txt` (`sqlalchemy`, `alembic`, `psycopg2-binary`).
  - Developers modifying models must execute `alembic revision --autogenerate` and `alembic upgrade head`.
