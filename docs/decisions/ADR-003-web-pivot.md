# ADR-003: Architecture Pivot to Unified Server-Rendered Web Application

**Date:** 2026-11-16  
**Status:** Accepted  
**Supercedes:** Desktop UI selection in ADR-001  

## Context

In ADR-001, separate PySide6 desktop applications (`apps/teacher` and `apps/student`) were selected for initial desktop prototyping. During faculty review and Voice of Stakeholder analysis (VoS-01 through VoS-17), significant production limitations emerged:
1. **Deployment & Installation Friction:** Distributing desktop binaries (requiring Python runtimes and 150MB+ Qt wheel dependencies) to dozens of diverse student personal laptops (Windows, macOS, Linux) introduced severe friction and environment failure rates in real classroom settings.
2. **Real-Time Assessment Disconnect:** Students taking in-class quizzes require an immediate, zero-install interface accessible via standard web browsers on laptops, tablets, or phones.
3. **Single Point of Maintenance:** Maintaining distinct PySide6 desktop codebases alongside a FastAPI backend required duplicate data validation and synchronization logic.
4. **Professor Mandate:** The academic project must represent a production-ready software solution rather than a toy desktop prototype.

## Decision

We pivot the user-facing interface from separate PySide6 desktop clients to a **single unified web application**:
- **Framework:** FastAPI serving server-rendered HTML via **Jinja2 templates**.
- **Styling:** Modern, accessible, responsive CSS (`frontend/static/css/style.css`) with zero heavy JavaScript framework dependencies.
- **Client Interactions:** Vanilla JavaScript (`frontend/static/js/app.js`) handling Q06 Poka-Yoke confirmation modals, double-submission blocking, dynamic question forms, and flash alert dismissal.
- **Decommissioning:** The legacy `apps/` desktop directory is permanently retired from the repository.

## Consequences

- **Positive:**
  - **Zero Student Install:** Students participate instantly by visiting `/join` on any web browser.
  - **Unified Runtime:** A single command (`uvicorn backend.main:app`) runs the entire frontend and backend server.
  - **Full Q06 Visual Feedback:** Pre-add validation and Search Before Add conflict alerts render seamlessly as inline flash banners and responsive modals.
  - **Lower Maintenance Overhead:** Eliminates desktop packaging, OS-dependent Qt event loop issues, and cross-platform desktop UI testing bugs.
- **Negative / Trade-offs:**
  - Removed desktop Qt native widgets in favor of web standards.
  - Requires Jinja2 templating and form parsing dependencies (`python-multipart`).
