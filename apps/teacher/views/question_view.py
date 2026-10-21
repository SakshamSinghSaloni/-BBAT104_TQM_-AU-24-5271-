"""
PySide6 View for Question CRUD operations inside a selected Quiz.

Enforces:
- Q06 Feature 4: Confirmation Dialogs before deleting questions
- Q06 Feature 2: Client-side and server-side pre-add validation for MCQ options
"""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.teacher.api_client import APIClient


class QuestionView(QWidget):
    def __init__(self, api_client: APIClient, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.current_quiz_id: Optional[int] = None
        self.current_quiz_title: str = ""
        self._setup_ui()

    def set_active_quiz(self, quiz_id: int, quiz_title: str):
        self.current_quiz_id = quiz_id
        self.current_quiz_title = quiz_title
        self.header_label.setText(f"<h2>Questions for Quiz #{quiz_id}: {quiz_title}</h2>")
        self.refresh_questions()

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Add Question Form
        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)

        self.header_label = QLabel("<h2>Questions Management</h2><p><i>Select a quiz from the Quizzes tab first.</i></p>")
        form_layout.addWidget(self.header_label)

        form_layout.addWidget(QLabel("<b>Question Prompt:</b>"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter the question text here...")
        self.text_input.setMaximumHeight(70)
        form_layout.addWidget(self.text_input)

        form_layout.addWidget(QLabel("<b>Question Type:</b>"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["mcq", "true_false", "short_answer"])
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        form_layout.addWidget(self.type_combo)

        # Options input container (for MCQ)
        self.options_container = QWidget()
        options_layout = QVBoxLayout(self.options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.addWidget(QLabel("<b>MCQ Options (comma-separated):</b>"))
        self.options_input = QLineEdit()
        self.options_input.setPlaceholderText("e.g. Option A, Option B, Option C, Option D")
        options_layout.addWidget(self.options_input)
        form_layout.addWidget(self.options_container)

        # Text Correct Answer container (for MCQ and short_answer)
        self.text_answer_container = QWidget()
        text_ans_layout = QVBoxLayout(self.text_answer_container)
        text_ans_layout.setContentsMargins(0, 0, 0, 0)
        self.answer_label = QLabel("<b>Correct Answer:</b>")
        text_ans_layout.addWidget(self.answer_label)
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Must exactly match one of the options above")
        text_ans_layout.addWidget(self.answer_input)
        form_layout.addWidget(self.text_answer_container)

        # True/False Radio Buttons container (for true_false)
        self.tf_container = QWidget()
        tf_layout = QVBoxLayout(self.tf_container)
        tf_layout.setContentsMargins(0, 0, 0, 0)
        tf_layout.addWidget(QLabel("<b>Correct Answer:</b>"))
        tf_radios = QHBoxLayout()
        self.radio_true = QRadioButton("True")
        self.radio_false = QRadioButton("False")
        self.radio_true.setChecked(True)
        self.tf_group = QButtonGroup(self)
        self.tf_group.addButton(self.radio_true)
        self.tf_group.addButton(self.radio_false)
        tf_radios.addWidget(self.radio_true)
        tf_radios.addWidget(self.radio_false)
        tf_radios.addStretch()
        tf_layout.addLayout(tf_radios)
        form_layout.addWidget(self.tf_container)

        # Initialize to MCQ view
        self.tf_container.setVisible(False)

        points_layout = QHBoxLayout()
        points_layout.addWidget(QLabel("<b>Points:</b>"))
        self.points_spin = QSpinBox()
        self.points_spin.setRange(1, 100)
        self.points_spin.setValue(1)
        points_layout.addWidget(self.points_spin)
        points_layout.addStretch()
        form_layout.addLayout(points_layout)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Question")
        self.add_btn.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 6px;")
        self.add_btn.clicked.connect(self._on_add_question)
        btn_layout.addWidget(self.add_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_layout.addWidget(self.clear_btn)
        form_layout.addLayout(btn_layout)

        form_layout.addStretch()

        # Right panel: Table of Questions
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)

        table_header = QHBoxLayout()
        table_header.addWidget(QLabel("<h3>Quiz Questions List</h3>"))
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_questions)
        table_header.addWidget(refresh_btn)
        table_layout.addLayout(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Question Text", "Type", "Correct Answer", "Points"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        table_layout.addWidget(self.table)

        self.delete_btn = QPushButton("🗑️ Delete Selected Question")
        self.delete_btn.setStyleSheet("background-color: #E74C3C; color: white; font-weight: bold; padding: 6px;")
        self.delete_btn.clicked.connect(self._on_delete_question)
        table_layout.addWidget(self.delete_btn)

        layout.addWidget(form_panel, 1)
        layout.addWidget(table_panel, 2)

    def _on_type_changed(self, q_type: str):
        """Poka-Yoke dynamic form adaptation based on question type."""
        if q_type == "mcq":
            self.options_container.setVisible(True)
            self.text_answer_container.setVisible(True)
            self.tf_container.setVisible(False)
            self.answer_label.setText("<b>Correct Answer:</b>")
            self.answer_input.setPlaceholderText("Must exactly match one of the options above")
        elif q_type == "true_false":
            self.options_container.setVisible(False)
            self.text_answer_container.setVisible(False)
            self.tf_container.setVisible(True)
        elif q_type == "short_answer":
            self.options_container.setVisible(False)
            self.text_answer_container.setVisible(True)
            self.tf_container.setVisible(False)
            self.answer_label.setText("<b>Expected Answer (Single word or phrase):</b>")
            self.answer_input.setPlaceholderText("Enter the exact correct answer/phrase...")

    def _clear_form(self):
        self.text_input.clear()
        self.options_input.clear()
        self.answer_input.clear()
        self.radio_true.setChecked(True)
        self.points_spin.setValue(1)

    def refresh_questions(self):
        if not self.current_quiz_id:
            return
        try:
            questions = self.api_client.list_questions(self.current_quiz_id)
            self.table.setRowCount(len(questions))
            for row_idx, q in enumerate(questions):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(q["id"])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(q["question_text"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(q["question_type"]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(q["correct_answer"]))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(q["points"])))
        except Exception:
            pass

    def _on_add_question(self):
        if not self.current_quiz_id:
            QMessageBox.warning(self, "No Quiz Selected", "Please select a quiz first from the Quizzes tab.")
            return

        text = self.text_input.toPlainText().strip()
        q_type = self.type_combo.currentText()
        points = self.points_spin.value()

        # Q06 Pre-add Validation checks
        if not text:
            QMessageBox.warning(self, "Validation Error (Q06)", "Question text cannot be empty!")
            return

        options = None
        answer = ""

        if q_type == "mcq":
            raw_opts = self.options_input.text().strip()
            answer = self.answer_input.text().strip()
            if not answer:
                QMessageBox.warning(self, "Validation Error (Q06)", "Correct answer cannot be empty!")
                return
            options = [opt.strip() for opt in raw_opts.split(",") if opt.strip()]
            if len(options) < 2:
                QMessageBox.warning(self, "Validation Error (Q06)", "MCQ questions must have at least 2 options (comma-separated).")
                return
            if answer not in options:
                QMessageBox.warning(
                    self,
                    "Validation Error (Q06)",
                    f"Correct answer '{answer}' must exactly match one of the options: {options}"
                )
                return

        elif q_type == "true_false":
            options = ["True", "False"]
            answer = "True" if self.radio_true.isChecked() else "False"

        elif q_type == "short_answer":
            answer = self.answer_input.text().strip()
            if not answer:
                QMessageBox.warning(self, "Validation Error (Q06)", "Expected answer cannot be empty!")
                return
            options = None

        try:
            res = self.api_client.add_question(
                quiz_id=self.current_quiz_id,
                question_text=text,
                question_type=q_type,
                options=options,
                correct_answer=answer,
                points=points,
            )
            QMessageBox.information(self, "Success", f"Question added successfully with ID #{res['id']}!")
            self._clear_form()
            self.refresh_questions()
        except Exception as exc:
            err_msg = str(exc)
            if "409" in err_msg or "already exists" in err_msg:
                QMessageBox.warning(
                    self,
                    "Duplicate Question Detected (Q06: Search Before Add)",
                    f"This question prompt already exists in this quiz!\n\n"
                    "Duplicate questions are blocked to ensure quiz integrity.",
                )
            else:
                QMessageBox.critical(self, "Error", f"Failed to add question: {exc}")

    def _on_delete_question(self):
        """Enforces Q06 Feature 4: Confirmation Dialogs."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select a question to delete.")
            return

        row = selected_rows[0].row()
        q_id = int(self.table.item(row, 0).text())
        q_text = self.table.item(row, 1).text()

        # Q06 Feature 4: Confirmation Dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion (Q06 Feature 4)",
            f"Are you sure you want to delete Question #{q_id}?\n\n\"{q_text[:80]}...\"",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.api_client.delete_question(q_id)
                QMessageBox.information(self, "Deleted", "Question deleted successfully.")
                self.refresh_questions()
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to delete question: {exc}")
