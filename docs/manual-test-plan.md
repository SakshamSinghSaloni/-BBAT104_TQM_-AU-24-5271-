# Manual Test Plan & UI Verification Specification

**Project:** Online Quiz Assessment Platform  
**Scope:** Stage 6 Verification & Quality Audit  
**Document Version:** 1.0 | **Date:** 2026-11-16  

---

## 1. Overview & Objectives

While automated regression tests (52 tests across unit, repository, and API layers) verify data contracts and boundary logic, this **Manual Test Plan** validates client-rendered browser workflows, visual notifications, accessibility, user-feedback banners, and interactive modal dialogs.

All test scenarios utilize clean, generic data to validate production readiness.

---

## 2. Test Execution Environment

| Parameter | Value |
|-----------|-------|
| **Application Host** | `http://127.0.0.1:8000` |
| **Tested Browsers** | Google Chrome, Mozilla Firefox, Microsoft Edge |
| **Persistence Engine** | SQLite (Development) / PostgreSQL (Production) via SQLAlchemy 2.0 |
| **Active Session Code** | `TQM101` (Pre-seeded demo session) |

---

## 3. Manual Test Cases & Execution Matrix

### 3.1 Authentication & Instructor Account Management

#### TC-MAN-01: Instructor Account Registration
- **Category:** Authentication & Pre-Add Validation
- **Preconditions:** Server is running; user is at `/auth/register`.
- **Steps:**
  1. Enter Full Name: `Prof. Jane Doe`.
  2. Enter Email: `jane.doe@example.edu`.
  3. Enter Password: `password123` (valid >= 6 characters).
  4. Click `Create Account`.
- **Expected Outcome:** User is registered, signed session cookie (`quiz_session`) is set, and browser is redirected to `/dashboard` displaying `Welcome back, Prof. Jane Doe`.
- **Status:** **PASS**

#### TC-MAN-02: Duplicate Email Registration Prevention
- **Category:** Duplicate Prevention & Flash Messaging
- **Preconditions:** An account with email `jane.doe@example.edu` already exists.
- **Steps:**
  1. Navigate to `/auth/register`.
  2. Enter Full Name: `Dr. Duplicate User`.
  3. Enter Email: `jane.doe@example.edu`.
  4. Enter Password: `password123`.
  5. Click `Create Account`.
- **Expected Outcome:** Registration is halted; page re-renders with a prominent red danger alert: `An account with email 'jane.doe@example.edu' already exists.` No second record is created in the database.
- **Status:** **PASS**

#### TC-MAN-03: Instructor Login & Session Logout
- **Category:** Session Lifecycle & Authorization
- **Preconditions:** Instructor account exists.
- **Steps:**
  1. Navigate to `/auth/login`.
  2. Enter `teacher@university.edu` and `password123`.
  3. Click `Sign In`.
  4. Verify redirect to `/dashboard` and user pill `👤 Prof. Alex Smith` in navbar.
  5. Click `Logout` in the navbar.
- **Expected Outcome:** Cookie is cleared; redirected to `/auth/login`. Visiting `/dashboard` directly redirects immediately back to `/auth/login`.
- **Status:** **PASS**

---

### 3.2 Quiz & Assessment Authoring

#### TC-MAN-04: Quiz Creation with Title Validation
- **Category:** Pre-Add Validation
- **Preconditions:** Instructor is logged in and on `/quizzes`.
- **Steps:**
  1. Enter Title: `Computer Architecture Fundamentals`.
  2. Enter Description: `Midterm assessment covering CPU pipelining and memory cache hierarchy.`
  3. Click `+ Add Quiz`.
- **Expected Outcome:** Quiz is created and immediately appears in the Existing Quizzes table with `0 questions`.
- **Status:** **PASS**

#### TC-MAN-05: Duplicate Quiz Title Rejection
- **Category:** Duplicate Prevention & Conflict Handling
- **Preconditions:** Quiz with title `Computer Architecture Fundamentals` exists.
- **Steps:**
  1. On `/quizzes`, enter Title: `computer architecture fundamentals` (case variation, trailing spaces).
  2. Click `+ Add Quiz`.
- **Expected Outcome:** Submission is intercepted by duplicate check; page displays a danger alert: `A quiz with title 'computer architecture fundamentals' already exists... Duplicate quizzes are not allowed.`
- **Status:** **PASS**

#### TC-MAN-06: Question Authoring across Types (MCQ, True/False, Short Answer)
- **Category:** Question Management & Dynamic UI
- **Preconditions:** Instructor is on `/quizzes/{id}/questions`.
- **Steps:**
  1. **MCQ:** Select `Multiple Choice (MCQ)`. Enter prompt: `What is the main purpose of CPU cache?`. Fill options A, B, C, D. Select radio for option A. Click `+ Add Question`.
  2. **True/False:** Select `True / False`. Enter prompt: `L1 cache is typically faster than RAM.`. Select `True`. Click `+ Add Question`.
  3. **Short Answer:** Select `Short Answer`. Enter prompt: `Name the memory unit holding currently executing instructions.`. Expected: `Instruction Register`. Click `+ Add Question`.
- **Expected Outcome:** All 3 questions render in the questions list with correct badges (`MCQ`, `TRUE_FALSE`, `SHORT_ANSWER`), correct points, and green-highlighted correct answers.
- **Status:** **PASS**

#### TC-MAN-07: Safe Deletion with Confirmation Modal
- **Category:** Confirmation Modals
- **Preconditions:** A question or quiz exists with a `Delete` button.
- **Steps:**
  1. Click `Delete` on any question.
  2. Observe the modal dialog overlay: title `Confirm Action`, message `Are you sure you want to perform this action?`.
  3. Click `Cancel`. Verify the item is NOT deleted.
  4. Click `Delete` again, then click `Confirm`.
- **Expected Outcome:** Modal executes the delete request; item is removed from table; child foreign keys cascade without database error.
- **Status:** **PASS**

---

### 3.3 Live Session & Student Assessment Flow

#### TC-MAN-08: Launching Live Assessment Session
- **Category:** Session Administration
- **Preconditions:** Instructor is logged in.
- **Steps:**
  1. On `/quizzes`, click `Launch Session` on any quiz.
- **Expected Outcome:** System generates a collision-free 6-character session code (e.g. `83SSEY`), creates an active session, and redirects to `/sessions/{id}/results`.
- **Status:** **PASS**

#### TC-MAN-09: Student Session Entry (Zero-Friction Join)
- **Category:** Student Portal & Validation
- **Preconditions:** Active session code exists.
- **Steps:**
  1. Open a browser window (or incognito) at `/join`.
  2. Enter Session Code: (active code, e.g. `TQM101`).
  3. Enter Full Name: `Alex Morgan`.
  4. Enter Student ID: `STU-1001`.
  5. Click `Enter Assessment Room`.
- **Expected Outcome:** Student participant is registered and redirected to `/session/TQM101/take?participant_id={id}` displaying the assessment title, student name, and questions without leaking correct answers.
- **Status:** **PASS**

#### TC-MAN-10: Duplicate Student Join Rejection
- **Category:** Duplicate Prevention
- **Preconditions:** Student `STU-1001` has already joined session `TQM101`.
- **Steps:**
  1. Open `/join` in another tab.
  2. Enter Session Code: `TQM101`.
  3. Enter Name: `Alex Morgan`.
  4. Enter Student ID: `STU-1001`.
  5. Click `Enter Assessment Room`.
- **Expected Outcome:** System rejects the entry; displays danger alert: `Student ID 'STU-1001' has already joined session 'TQM101'.`
- **Status:** **PASS**

#### TC-MAN-11: Assessment Submission & Immediate Auto-Grading
- **Category:** Test Taking & Auto-Grading
- **Preconditions:** Student is on `/session/{code}/take`.
- **Steps:**
  1. Select answers for all questions.
  2. Click `Submit Quiz Answers`.
  3. On the confirmation modal, click `Confirm`.
- **Expected Outcome:** Form submits; button disables to prevent double-submitting; redirected to `/session/{code}/results?participant_id={id}` displaying:
  - Evaluation complete badge
  - Total score / Max score
  - Accuracy percentage
  - Detailed question-by-question breakdown showing student's submitted answer vs correct answer with points awarded.
- **Status:** **PASS**

#### TC-MAN-12: Duplicate Quiz Submission Prevention
- **Category:** Duplicate Prevention
- **Preconditions:** Student has completed and submitted the quiz in TC-MAN-11.
- **Steps:**
  1. Use browser back button or manually navigate to `/session/{code}/take?participant_id={id}`.
- **Expected Outcome:** System automatically detects existing submission and redirects directly to `/session/{code}/results?participant_id={id}`. Submitting a duplicate payload via POST returns HTTP 409 Conflict.
- **Status:** **PASS**

---

## 4. Verification Summary

| Metric | Target | Verified Actual |
|--------|--------|-----------------|
| **Automated Tests** | $\ge 45$ | **52 Passing (100%)** |
| **Manual Test Cases** | $\ge 10$ | **12 Executed & Verified (100% Pass)** |
| **Duplicate Prevention Layers** | 4 Tiers | **Storage, Pre-Add, Service, and UI Modals Verified** |
| **Cross-Browser Styling** | Responsive | **Consistent rendering across desktop & mobile viewport sizes** |
