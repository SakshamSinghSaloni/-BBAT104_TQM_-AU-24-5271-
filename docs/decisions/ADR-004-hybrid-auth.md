# ADR-004: Hybrid Authentication Model (Teacher Identity vs Ephemeral Student Sessions)

**Date:** 2026-11-16  
**Status:** Accepted  

## Context

The Online Quiz System must accommodate two distinct stakeholder archetypes with opposing security and usability requirements:
1. **Instructors (SH-01, SH-03):** Require persistent account credentials, secure password protection, identity tracking, and authorization to create, modify, and delete quizzes and launch sessions.
2. **Students (SH-02):** Need immediate entry into timed quizzes during lectures or exams without registration friction, forgotten passwords, email verification delays, or account provisioning overhead.
3. **Q06 Anti-Duplicate Requirement:** Despite the absence of permanent student user accounts, the system must strictly guarantee that no student can submit multiple times or join a session twice with the same identifier.

## Decision

We adopt a **Hybrid Authentication Model**:

| User Role | Authentication Mechanism | Session Management | Storage & Q06 Guard |
|-----------|--------------------------|---------------------|----------------------|
| **Instructor / Admin** | Credentialed Login (Email + Password) | Tamper-proof HTTP-Only Cookie signed with `itsdangerous` URLSafeTimedSerializer | Stored in `users` table; password hashed with `bcrypt`; unique email constraint (`ix_users_email`). |
| **Student** | Ephemeral Join (Name + Roll Number + Session Code) | Ephemeral Participant ID in query/form state | Stored in `participants` table; strictly guarded by composite unique constraint `uq_session_participant (session_id, student_identifier)`. |

### Student Assessment Lifecycle
1. Student navigates to `/join` (or follows session link `?code=ABC123`).
2. Enters Name, Roll Number, and Session Code.
3. System validates:
   - Session code exists and status is `active`.
   - Roll number has not already joined this session (Q06 Search Before Add).
4. System creates ephemeral `Participant` record and redirects to `/session/{code}/take?participant_id={id}`.
5. On quiz submission:
   - System verifies participant belongs to session and has not already submitted (Q06 Search Before Add & `uq_participant_question`).
   - Answers are graded and recorded in `submissions`.
   - Student is redirected to `/session/{code}/results?participant_id={id}`.

### Instructor Security
- Endpoints under `/dashboard`, `/quizzes`, and `/sessions/{id}/results` require valid session cookie decoded by `get_current_user_optional`.
- REST API mutations require valid session cookie or Bearer token decoded by `get_current_user`.
- Passwords are encrypted with 12 rounds of salted `bcrypt`.

## Consequences

- **Positive:**
  - Maximum usability: Zero account setup barrier for classroom students.
  - Rock-solid security: Instructors' quizzes and administrative controls are protected behind authenticated sessions.
  - Zero-defect duplicate prevention: Enforces Q06 across both authenticated and ephemeral domains.
- **Negative / Trade-offs:**
  - Student participant history is session-bound rather than unified under a permanent student user profile (which satisfies the university quiz assessment model).
