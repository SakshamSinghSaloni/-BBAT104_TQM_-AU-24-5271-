# Stakeholder Register: Online Quiz System

**Course:** BBAT104 — Fundamentals of Total Quality Management (TQM)  
**Academic Session:** 2026–27  
**Student:** Saksham Singh Saloni (Roll No: AU-24-5271)  
**Project Baseline:** Baseline No. 9 — Online Quiz System  
**Assigned Quality Goal:** Q06 — Reduce Duplicate Entries  
**Document Version:** 1.0  
**Date:** 2026-11-16  

---

## 1. Executive Summary & TQM Context

In Total Quality Management (TQM), quality is defined by satisfying customer and stakeholder requirements through process discipline and continuous improvement. Software projects often fail to achieve quality goals when requirements are gathered solely from direct operators while ignoring secondary and institutional stakeholders.

Following the quality pipeline prescribed for this project:
$$\text{Identify Stakeholders} \longrightarrow \text{Capture Voices (VoS)} \longrightarrow \text{Derive SRS} \longrightarrow \text{Implement System} \longrightarrow \text{Verify \& Test} \longrightarrow \text{Log Defects} \longrightarrow \text{TQM Analysis}$$

This document executes **Stage 1: Stakeholder Identification**. It establishes a formal Stakeholder Register identifying all internal and external parties with an interest in the Online Quiz System, detailing their roles, operational impact, expectations, and relevance to **Quality Goal Q06 (Reduce Duplicate Entries)**.

---

## 2. Comprehensive Stakeholder Register

| Stakeholder ID | Stakeholder Name | Category | Primary Role / Responsibility | Key Quality Interest / Expectation | Q06 Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SH-01** | **Teacher / Quiz Conductor** | Primary User (Internal Customer) | Creates and manages quizzes, authors questions, initiates sessions, monitors progress, and exports grades. | Efficiency in assessment creation, zero data loss, unambiguous UI, prevention of accidental quiz/question duplication. | **High:** Primary beneficiary of Search-Before-Add and confirmation prompts to prevent duplicate quizzes or identical questions. |
| **SH-02** | **Student / Participant** | Primary User (External Customer) | Joins active quiz sessions via session codes, submits answers under time constraints, and reviews feedback. | Fair, deterministic evaluation; error-free submission handling; zero duplicate session joins; robust auto-grading. | **High:** Dependent on storage-level uniqueness to prevent double submissions or duplicate participant records. |
| **SH-03** | **Professor / Course Evaluator** | Project Sponsor & Customer | Evaluates academic deliverables against TQM principles (ISO 9001 / Six Sigma frameworks) and syllabus rubric. | Strict adherence to TQM pipeline, end-to-end traceability, empirical defect logging, statistical quality control (SQC). | **High:** Requires demonstrable multi-layered defense against duplicate entries with verifiable test evidence. |
| **SH-04** | **University / Academic Institution** | Regulatory / Governance Body | Enforces academic integrity, grading standardization, data privacy, and institutional audit standards. | Reliable audit trails, tamper-proof score records, prevention of fraudulent duplicate submissions, high availability. | **Medium:** Institutional compliance depends on database uniqueness and data integrity constraints. |
| **SH-05** | **Software Developer (Student)** | Internal (Project Creator) | Designs, implements, refactors, tests, and maintains the application architecture, code, and documentation. | Maintainable layered architecture, rapid test execution, clean separation of concerns, CI/CD compatibility. | **High:** Responsible for translating Q06 requirements into database constraints, Pydantic schemas, and service logic. |
| **SH-06** | **System Administrator / DevOps** | Support & Operations | Manages hosting environment, database provisioning, migration deployment, backups, and health monitoring. | Production readiness, concurrent database access, reproducible migrations (Alembic), low maintenance overhead. | **Medium:** Needs relational integrity enforced at the storage engine level so bad data cannot corrupt the database. |

---

## 3. Detailed Stakeholder Profiles

### 3.1 SH-01: Teacher / Quiz Conductor
- **Profile:** Faculty members and instructors responsible for creating assessments to evaluate student learning outcomes.
- **Pain Points:** Accidental double-clicks creating duplicate quizzes; pasting identical questions across multiple rounds; accidental deletion of question banks without confirmation.
- **Critical Success Factors:**
  1. Instant notification if an existing quiz has the same or similar title (Search Before Add).
  2. Immediate rejection when attempting to insert an identical question into the same quiz.
  3. Mandatory interactive confirmation before deleting quizzes or questions (Poka-Yoke / Error Proofing).

### 3.2 SH-02: Student / Participant
- **Profile:** Undergraduates taking timed evaluations from varying network conditions and devices.
- **Pain Points:** Network lag causing duplicate submit clicks; session timeout re-joins creating conflicting participant records; grade penalties due to case mismatches in short-answer questions.
- **Critical Success Factors:**
  1. Strict composite uniqueness ensuring one participant per session identifier (`uq_session_participant`).
  2. Idempotent submission endpoint ensuring one answer record per question per participant (`uq_participant_question`).
  3. Case-insensitive, whitespace-trimmed evaluation for objective short-answer questions.

### 3.3 SH-03: Professor / Course Evaluator
- **Profile:** TQM faculty evaluating project execution across Reviews 1 through 4.
- **Pain Points:** Disjointed project deliverables where code does not reflect the SRS, or where quality tools (FMEA, Pareto) use fictional data rather than real test findings.
- **Critical Success Factors:**
  1. Full traceability matrix: $\text{Voice} \rightarrow \text{SRS Requirement} \rightarrow \text{Source Module} \rightarrow \text{Test Case} \rightarrow \text{TQM Defect Log}$.
  2. Verifiable test suite demonstrating $\ge 100\%$ automated coverage of assigned quality goal features.
  3. Seamless transition from desktop prototype to production-grade web architecture.

### 3.4 SH-04: University / Academic Institution
- **Profile:** University administration and accreditation boards (e.g., NAAC / NBA / UGC).
- **Pain Points:** Grade manipulation, duplicate grade postings, inconsistent assessment records across departments.
- **Critical Success Factors:**
  1. Relational database constraints enforcing strict foreign key cascade rules and ACID compliance.
  2. Immutable timestamping for all quiz creations, session starts, and student submissions.

### 3.5 SH-05: Software Developer (Student Author)
- **Profile:** Single student engineer responsible for end-to-end delivery under academic timelines.
- **Pain Points:** Brittle architectures, monolithic scripts where database changes break UI code, slow test suites.
- **Critical Success Factors:**
  1. Layered architecture: decoupled API, Service, Repository, and Database layers.
  2. Reusable validation models (Pydantic) and declarative schema models (SQLAlchemy ORM).
  3. Fast, automated unit and integration tests executing in under 2 seconds.

### 3.6 SH-06: System Administrator / DevOps
- **Profile:** Operational role responsible for keeping the assessment platform online, secure, and performant during peak exam loads.
- **Pain Points:** SQLite database lock errors under concurrent multi-user writes; schema migrations requiring manual SQL scripts on production servers.
- **Critical Success Factors:**
  1. Migration to concurrent relational database (PostgreSQL) with connection pooling.
  2. Version-controlled schema migrations via Alembic.
  3. Standardized health-check endpoints (`GET /`) and structured logging.

---

## 4. Stakeholder Power vs. Interest Grid (Mendelow's Matrix)

To prioritize quality requirements and manage project communications, stakeholders are mapped across the **Power vs. Interest Grid**:

```mermaid
quadrantChart
    title Stakeholder Power vs. Interest Matrix
    x-axis Low Interest --> High Interest
    y-axis Low Power --> High Power
    quadrant-1 Manage Closely (Key Players)
    quadrant-2 Keep Satisfied
    quadrant-3 Monitor (Minimum Effort)
    quadrant-4 Keep Informed
    "SH-01: Teacher": [0.85, 0.75]
    "SH-02: Student": [0.80, 0.40]
    "SH-03: Professor": [0.95, 0.95]
    "SH-04: University": [0.35, 0.85]
    "SH-05: Developer": [0.90, 0.60]
    "SH-06: SysAdmin": [0.55, 0.50]
```

### Engagement Strategy by Quadrant:
1. **Manage Closely (High Power, High Interest):**
   - **SH-03 (Professor / Evaluator):** Direct stakeholder. Deliverables must precisely match academic rubrics and TQM methodologies.
   - **SH-01 (Teacher / Conductor):** Primary operator. Workflows for creating, managing, and conducting quizzes must be frictionless and error-proof.
2. **Keep Satisfied (High Power, Low/Moderate Interest):**
   - **SH-04 (University / Institution):** Enforce data integrity, security, and auditability at the architectural level.
3. **Keep Informed (Low Power, High Interest):**
   - **SH-02 (Student / Participant):** Ensure intuitive submission flow, immediate feedback, and transparent scoring rules.
   - **SH-05 (Developer):** Continuously align technical choices with course requirements.
4. **Monitor (Low Power, Moderate Interest):**
   - **SH-06 (SysAdmin / Operations):** Provide health checks, documentation, and standard environment configuration.

---

## 5. Next Steps: Traceability Forward

With Stage 1 complete, all downstream requirements and tests will be tagged with their originating Stakeholder ID (`SH-01` through `SH-06`). 

The immediate next step is **Stage 2: Voice of the Stakeholder (VoS)**, where:
1. Raw stakeholder statements will be collected.
2. Each statement will be analyzed using **CTQ (Critical to Quality)** trees to extract core customer needs.
3. Traceable VoS requirements (`VoS-01`, `VoS-02`, etc.) will be established to form the foundation of the rebuilt SRS.
