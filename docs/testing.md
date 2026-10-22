# Automated Testing Report & Evidence

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries  
**Course:** BBAT104 — Fundamentals of TQM  
**Student:** Saksham Singh Saloni (AU-24-5271)  
**Milestone:** Review 2 Verification  
**Test Framework:** `pytest` (v9.1.1) with Python 3.13.5  
**Execution Date:** 2026-10-11  

---

## 1. Executive Summary

| Metric | Value |
| :--- | :--- |
| **Total Tests Executed** | 23 |
| **Passed** | 23 (100%) |
| **Failed / Errors** | 0 |
| **Execution Time** | 1.11 seconds |
| **Target Review** | Review 2 (Base System & CRUD + Q06 Quality Goal + Auto-Grading) |

All core CRUD modules, auto-grading algorithms, and assigned Q06 quality-goal features have been validated through repeatable, automated unit and integration tests.

---

## 2. Test Execution Log (Verbatim Console Output)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AU\Notes\Semester 5\TQM\Project\BBAT104_TQM_[AU-24-5271]
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False
collected 23 items

tests/test_api.py::test_api_create_quiz_success PASSED                   [  4%]
tests/test_api.py::test_api_q06_pre_add_validation_rejects_empty_title PASSED [  8%]
tests/test_api.py::test_api_q06_search_before_add_rejects_duplicate_quiz PASSED [ 13%]
tests/test_api.py::test_api_list_quizzes PASSED                          [ 17%]
tests/test_api.py::test_api_update_quiz PASSED                           [ 21%]
tests/test_api.py::test_api_delete_quiz PASSED                           [ 26%]
tests/test_api.py::test_api_add_and_list_question PASSED                 [ 30%]
tests/test_api.py::test_api_q06_search_before_add_rejects_duplicate_question PASSED [ 34%]
tests/test_api.py::test_api_q06_pre_add_validation_question_options PASSED [ 39%]
tests/test_database.py::test_tables_created_successfully PASSED          [ 43%]
tests/test_database.py::test_foreign_key_cascade_deletion PASSED         [ 47%]
tests/test_database.py::test_q06_unique_session_code_constraint PASSED   [ 52%]
tests/test_database.py::test_q06_unique_participant_per_session_constraint PASSED [ 56%]
tests/test_grading.py::test_short_answer_case_insensitivity PASSED       [ 60%]
tests/test_grading.py::test_short_answer_whitespace_trimming PASSED      [ 65%]
tests/test_grading.py::test_short_answer_incorrect PASSED                [ 69%]
tests/test_grading.py::test_true_false_evaluation PASSED                 [ 73%]
tests/test_services.py::test_q06_pre_add_validation_quiz_empty_title PASSED [ 78%]
tests/test_services.py::test_q06_pre_add_validation_quiz_valid_clean PASSED [ 82%]
tests/test_services.py::test_q06_pre_add_validation_mcq_requires_options PASSED [ 86%]
tests/test_services.py::test_q06_pre_add_validation_mcq_answer_must_be_in_options PASSED [ 91%]
tests/test_services.py::test_q06_search_before_add_quiz_duplicate_detection PASSED [ 95%]
tests/test_services.py::test_q06_search_before_add_question_duplicate_in_quiz PASSED [100%]

======================== 23 passed in 1.11s ========================
```

---

## 3. Detailed Test Breakdown by Quality Feature

### 3.1 Q06 Feature 1: Unique ID Constraints
*Storage-level integrity enforcement in SQLite to prevent duplicate records.*

| Test Function | File | Description | Result |
| :--- | :--- | :--- | :---: |
| `test_q06_unique_session_code_constraint` | `tests/test_database.py` | Enforces `UNIQUE(session_code)` at DB level; rejects collisions with `sqlite3.IntegrityError`. | **PASS** |
| `test_q06_unique_participant_per_session_constraint` | `tests/test_database.py` | Enforces composite unique constraint `UNIQUE(session_id, student_identifier)`; prevents duplicate student joins. | **PASS** |
| `test_tables_created_successfully` | `tests/test_database.py` | Verifies schemas, primary keys, and auto-increment indices on all 5 tables. | **PASS** |
| `test_foreign_key_cascade_deletion` | `tests/test_database.py` | Verifies referential integrity and cascading delete rules (`PRAGMA foreign_keys = ON`). | **PASS** |

---

### 3.2 Q06 Feature 2: Pre-add Validation
*Sanitizing and validating payloads before data reaches the persistence layer.*

| Test Function | File | Description | Result |
| :--- | :--- | :--- | :---: |
| `test_q06_pre_add_validation_quiz_empty_title` | `tests/test_services.py` | Pydantic validator rejects empty or whitespace-only quiz titles. | **PASS** |
| `test_q06_pre_add_validation_quiz_valid_clean` | `tests/test_services.py` | Verifies automatic whitespace trimming on valid titles and descriptions. | **PASS** |
| `test_q06_pre_add_validation_mcq_requires_options` | `tests/test_services.py` | Requires multiple-choice questions to supply an options list. | **PASS** |
| `test_q06_pre_add_validation_mcq_answer_must_be_in_options` | `tests/test_services.py` | Validates that `correct_answer` strictly matches one of the declared options. | **PASS** |
| `test_api_q06_pre_add_validation_rejects_empty_title` | `tests/test_api.py` | FastAPI returns HTTP `422 Unprocessable Entity` for invalid quiz creation. | **PASS** |
| `test_api_q06_pre_add_validation_question_options` | `tests/test_api.py` | FastAPI returns HTTP `422` when question answers do not match option lists. | **PASS** |

---

### 3.3 Q06 Feature 3: Search Before Add
*Detecting near-duplicates or existing matches before insertion.*

| Test Function | File | Description | Result |
| :--- | :--- | :--- | :---: |
| `test_q06_search_before_add_quiz_duplicate_detection` | `tests/test_services.py` | Service searches existing quizzes by case-insensitive title and attaches an advisory duplicate warning. | **PASS** |
| `test_q06_search_before_add_question_duplicate_in_quiz` | `tests/test_services.py` | Service searches questions in the parent quiz and attaches duplicate warning when identical prompt text is detected. | **PASS** |

---

### 3.4 Q06 Feature 4: Confirmation Dialogs
*Client-side protection against accidental destructive actions.*

- Implemented in `apps/teacher/views/quiz_view.py` (`_on_delete_quiz` method).
- Implemented in `apps/teacher/views/question_view.py` (`_on_delete_question` method).
- Utilizes `PySide6.QtWidgets.QMessageBox.question` with `QMessageBox.Yes | QMessageBox.No` default `No` safety lock before dispatching any `DELETE` request.

---

### 3.5 Core CRUD Modules (Quizzes & Questions)

| Test Function | File | Operation Verified | Result |
| :--- | :--- | :--- | :---: |
| `test_api_create_quiz_success` | `tests/test_api.py` | **Create** Quiz (`POST /api/quizzes` $\rightarrow$ 201 Created) | **PASS** |
| `test_api_list_quizzes` | `tests/test_api.py` | **Read** All Quizzes (`GET /api/quizzes` $\rightarrow$ 200 OK) | **PASS** |
| `test_api_update_quiz` | `tests/test_api.py` | **Update** Quiz (`PUT /api/quizzes/{id}` $\rightarrow$ 200 OK) | **PASS** |
| `test_api_delete_quiz` | `tests/test_api.py` | **Delete** Quiz (`DELETE /api/quizzes/{id}` $\rightarrow$ 200 OK) | **PASS** |
| `test_api_add_and_list_question` | `tests/test_api.py` | **Create & Read** Question (`POST/GET /api/quizzes/{id}/questions`) | **PASS** |

---

### 3.6 Auto-Grading & Case-Insensitive Evaluation (Customer Focus / Poka-Yoke)

| Test Function | File | Operation Verified | Result |
| :--- | :--- | :--- | :---: |
| `test_short_answer_case_insensitivity` | `tests/test_grading.py` | Verifies short answers match regardless of casing (`python` == `Python` == `PYTHON`). | **PASS** |
| `test_short_answer_whitespace_trimming` | `tests/test_grading.py` | Verifies leading and trailing whitespaces are trimmed prior to evaluation. | **PASS** |
| `test_short_answer_incorrect` | `tests/test_grading.py` | Confirms actually incorrect short answers receive 0 points with helpful feedback. | **PASS** |
| `test_true_false_evaluation` | `tests/test_grading.py` | Verifies robust normalized boolean matching for True/False questions. | **PASS** |

---

## 4. How to Reproduce

In the project root with the virtual environment activated:

```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```
