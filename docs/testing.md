# Automated Testing Report & Evidence

**Project:** Online Quiz System — Q06: Reduce Duplicate Entries  
**Course:** BBAT104 — Fundamentals of TQM  
**Student:** Saksham Singh Saloni (AU-24-5271)  
**Milestone:** Review 2 Verification  
**Test Framework:** `pytest` (v9.1.1) with Python 3.13.5  
**Execution Date:** 2026-10-22  

---

## 1. Executive Summary

| Metric | Value |
| :--- | :--- |
| **Total Tests Executed** | 29 |
| **Passed** | 29 (100%) |
| **Failed / Errors** | 0 |
| **Execution Time** | 1.22 seconds |
| **Target Review** | Review 2 (Base System & CRUD + Q06 Quality Goal + Auto-Grading) |

All core CRUD modules (create, read, update, delete for Quizzes and Questions), auto-grading algorithms, and assigned Q06 quality-goal features have been validated through repeatable, automated unit and integration tests.

---

## 2. Test Execution Log (Verbatim Console Output)

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0 -- D:\AU\Notes\Semester 5\TQM\Project\BBAT104_TQM_[AU-24-5271]\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\AU\Notes\Semester 5\TQM\Project\BBAT104_TQM_[AU-24-5271]
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False
collecting ... collected 29 items

tests/test_api.py::test_api_create_quiz_success PASSED                   [  3%]
tests/test_api.py::test_api_q06_pre_add_validation_rejects_empty_title PASSED [  6%]
tests/test_api.py::test_api_q06_search_before_add_rejects_duplicate_quiz PASSED [ 10%]
tests/test_api.py::test_api_list_quizzes PASSED                          [ 13%]
tests/test_api.py::test_api_update_quiz PASSED                           [ 17%]
tests/test_api.py::test_api_delete_quiz PASSED                           [ 20%]
tests/test_api.py::test_api_add_and_list_question PASSED                 [ 24%]
tests/test_api.py::test_api_q06_search_before_add_rejects_duplicate_question PASSED [ 27%]
tests/test_api.py::test_api_q06_pre_add_validation_question_options PASSED [ 31%]
tests/test_api.py::test_api_update_question PASSED                       [ 34%]
tests/test_api.py::test_api_delete_question PASSED                       [ 37%]
tests/test_api.py::test_api_update_question_rejects_answer_not_in_options PASSED [ 41%]
tests/test_api.py::test_api_update_quiz_rejects_duplicate_title PASSED   [ 44%]
tests/test_api.py::test_api_update_question_rejects_duplicate_text PASSED [ 48%]
tests/test_database.py::test_tables_created_successfully PASSED          [ 51%]
tests/test_database.py::test_foreign_key_cascade_deletion PASSED         [ 55%]
tests/test_database.py::test_q06_unique_session_code_constraint PASSED   [ 58%]
tests/test_database.py::test_q06_unique_participant_per_session_constraint PASSED [ 62%]
tests/test_grading.py::test_short_answer_case_insensitivity PASSED       [ 65%]
tests/test_grading.py::test_short_answer_whitespace_trimming PASSED      [ 68%]
tests/test_grading.py::test_short_answer_incorrect PASSED                [ 72%]
tests/test_grading.py::test_true_false_evaluation PASSED                 [ 75%]
tests/test_services.py::test_q06_pre_add_validation_quiz_empty_title PASSED [ 79%]
tests/test_services.py::test_q06_pre_add_validation_quiz_valid_clean PASSED [ 82%]
tests/test_services.py::test_q06_pre_add_validation_mcq_requires_options PASSED [ 86%]
tests/test_services.py::test_q06_pre_add_validation_mcq_answer_must_be_in_options PASSED [ 89%]
tests/test_services.py::test_q06_pre_add_validation_question_update_empty PASSED [ 93%]
tests/test_services.py::test_q06_search_before_add_quiz_duplicate_detection PASSED [ 96%]
tests/test_services.py::test_q06_search_before_add_question_duplicate_in_quiz PASSED [100%]

======================== 29 passed in 1.22s ========================
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
| `test_q06_pre_add_validation_question_update_empty` | `tests/test_services.py` | Pydantic validator rejects blank fields on QuestionUpdate. | **PASS** |
| `test_api_q06_pre_add_validation_rejects_empty_title` | `tests/test_api.py` | FastAPI returns HTTP `422 Unprocessable Entity` for invalid quiz creation. | **PASS** |
| `test_api_q06_pre_add_validation_question_options` | `tests/test_api.py` | FastAPI returns HTTP `422` when question answers do not match option lists. | **PASS** |
| `test_api_update_question_rejects_answer_not_in_options` | `tests/test_api.py` | Service validates on update that `correct_answer` is present in question options. | **PASS** |

---

### 3.3 Q06 Feature 3: Search Before Add
*Detecting near-duplicates or existing matches before insertion or updating.*

| Test Function | File | Description | Result |
| :--- | :--- | :--- | :---: |
| `test_q06_search_before_add_quiz_duplicate_detection` | `tests/test_services.py` | Service searches existing quizzes by case-insensitive title and blocks duplicate quiz creation. | **PASS** |
| `test_q06_search_before_add_question_duplicate_in_quiz` | `tests/test_services.py` | Service searches questions in parent quiz and blocks duplicate prompt creation. | **PASS** |
| `test_api_q06_search_before_add_rejects_duplicate_quiz` | `tests/test_api.py` | API returns HTTP `409 Conflict` when creating duplicate quiz title. | **PASS** |
| `test_api_q06_search_before_add_rejects_duplicate_question` | `tests/test_api.py` | API returns HTTP `409 Conflict` when creating duplicate question in same quiz. | **PASS** |
| `test_api_update_quiz_rejects_duplicate_title` | `tests/test_api.py` | API returns HTTP `409 Conflict` when updating quiz to an existing title. | **PASS** |
| `test_api_update_question_rejects_duplicate_text` | `tests/test_api.py` | API returns HTTP `409 Conflict` when updating question to match another prompt in quiz. | **PASS** |

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
| `test_api_update_question` | `tests/test_api.py` | **Update** Question (`PUT /api/questions/{id}` $\rightarrow$ 200 OK) | **PASS** |
| `test_api_delete_question` | `tests/test_api.py` | **Delete** Question (`DELETE /api/questions/{id}` $\rightarrow$ 200 OK) | **PASS** |

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
