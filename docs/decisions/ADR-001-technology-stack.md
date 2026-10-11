# ADR-001: Technology Stack Selection

**Date:** 2026-10-11
**Status:** Accepted

## Context

The BBAT104 course project requires building an Online Quiz System with CRUD functionality and Q06 duplicate-reduction features. The official guidelines suggest Python 3.x, Tkinter/CustomTkinter, SQLite3/Pandas, and Matplotlib/Seaborn. The professor confirmed that additional appropriate libraries are permitted.

The system must eventually support teacher and student clients communicating over the internet, meaning a client-server architecture is necessary.

## Decision

| Layer | Choice |
|-------|--------|
| Desktop UI | **PySide6** (Qt for Python) |
| Backend | **FastAPI** with **Uvicorn** |
| Database | **SQLite3** (backend-only access) |
| HTTP Client | **httpx** |
| Testing | **pytest** |
| Validation | **Pydantic** (via FastAPI) |

## Alternatives Considered

| Alternative | Reason for Rejection |
|-------------|---------------------|
| Tkinter | Limited widget set; difficult to build professional-looking interfaces; student preferred PySide6 |
| Flask | No built-in async support; no automatic request validation; manual schema documentation |
| Django | Too heavy for the project scope; ORM adds unnecessary complexity over direct SQLite |
| Direct SQLite in client | Cannot support multi-user access over a network; file-locking issues |
| PostgreSQL immediately | Requires separate server setup; SQLite is sufficient for development and initial reviews |

## Consequences

- PySide6 requires installation (~150MB) but provides a professional desktop toolkit.
- FastAPI provides automatic OpenAPI documentation, which serves as living API docs.
- The three-layer backend (API → Service → Repository) adds modest initial structure but pays off in maintainability and testability.
- SQLite can be swapped to PostgreSQL later by changing only the repository layer.
