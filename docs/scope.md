# Scope Definition

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries
**Version:** 1.0 | **Date:** 2026-10-11

---

## 1. Review 1 Deliverables (10 marks)

| Deliverable | Description | Status |
|-------------|------------|--------|
| GitHub repository | Public repository `BBAT104_TQM_[AU-24-5271]` initialized with structured layout | Planned |
| System Architecture Flowchart | Mermaid diagram showing client-server architecture, layers, and communication | Planned |
| SRS Document | Functional and non-functional requirements with IDs, acceptance criteria, traceability | Planned |
| Scope Definition | This document — clear boundaries for each review phase | Planned |

---

## 2. Review 2 Deliverables (15 marks)

### 2.1 Base CRUD Modules

| Module | Operations | Entities |
|--------|-----------|----------|
| Quiz Management | Create, Read (list + detail), Update, Delete | Quiz |
| Question Management | Create, Read (list + detail), Update, Delete | Question |

**Implementation scope:**
- Backend API endpoints (FastAPI) for all CRUD operations.
- Service layer with business logic and validation.
- Repository layer with SQL queries and transaction handling.
- SQLite database with schema, constraints, and foreign keys.
- Teacher desktop client (PySide6) providing a GUI for all CRUD operations.

### 2.2 Q06 Quality Goal Features (4 features)

| # | Feature | Scope |
|---|---------|-------|
| 1 | **Unique ID Constraints** | Database-level PRIMARY KEY, UNIQUE constraints, and composite unique keys preventing duplicate records |
| 2 | **Pre-add Validation** | Server-side validation of all required fields, data types, and acceptable ranges before any INSERT |
| 3 | **Search Before Add** | Service-layer duplicate-detection queries before creating records; documented duplicate definitions per entity |
| 4 | **Confirmation Dialogs** | PySide6 confirmation prompts before delete operations and other destructive actions |

### 2.3 Stretch goals for Review 2 (if time permits)

- Basic quiz session workflow: start session → join → submit → grade.
- Student desktop client (minimal).
- Session-related API endpoints.

---

## 3. Future Review Deliverables

### Review 3: FMEA & Risk Audit (15 marks)

- FMEA matrix with RPN = Severity × Occurrence × Detection.
- SIPOC process map for quiz system workflows.
- CTQ (Critical to Quality) tree.
- Defect logging using actual project defects.

### Review 4: SQC & Continuous Improvement (15 marks)

- Pareto chart (80/20 analysis) from defect data.
- Ishikawa (Fishbone) diagram for root-cause analysis.
- Checksheets for defect tracking.
- PDCA cycle documentation.

### Final Demonstration & Viva (10 marks)

- Live software demonstration.
- Bug-handling defense.
- Oral viva on TQM tool selections.

### Documentation & GitHub Health (5 marks)

- Comprehensive README with screenshots and setup instructions.
- User manual.
- ≥ 30 meaningful commits.
- GitHub Issues tracking.

---

## 4. Out of Scope

The following are **not** part of this project:

| Item | Reason |
|------|--------|
| Mobile applications | Desktop-only requirement |
| Exam proctoring / tab-switching detection | Beyond assignment scope |
| Payment or billing systems | Not relevant to quiz system |
| Third-party LMS integration | Not required |
| Complex role hierarchies (admin, moderator, etc.) | Only teacher and student roles needed |
| Advanced analytics dashboards | Not required for reviews; basic SQC charts suffice |
| Production-grade hosting and TLS | Architecturally supported but not a review requirement |
| Redis, message brokers, containers | No demonstrated need |

---

## 5. Duplicate Definition per Entity

This section documents what constitutes a "duplicate" for each entity, supporting the Q06 Search Before Add feature.

| Entity | Duplicate Condition | Enforcement |
|--------|-------------------|-------------|
| Quiz | No strict title uniqueness — teachers may create quizzes with similar titles. Exact duplicate detection is advisory. | Service-layer advisory warning (not blocking) |
| Question | Same quiz_id + identical question_text. Two questions with the same text in different quizzes are allowed. | Service-layer check before insert |
| Session | Same session_code (must be globally unique). Same quiz_id can have multiple sessions. | Database UNIQUE constraint |
| Participant | Same session_id + student_identifier. A student can participate in multiple different sessions. | Database UNIQUE constraint + service check |
| Submission | Same participant_id + question_id. One answer per question per participant. | Database UNIQUE constraint + service check |
