"""
PySide6 View for Quiz CRUD operations.

Enforces:
- Q06 Feature 4: Confirmation Dialogs before deleting quizzes
- Q06 Feature 3: Surface search/duplicate warning notices to the user
- Q06 Feature 2: Pre-add validation and input sanitization
"""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from apps.teacher.api_client import APIClient


class QuizView(QWidget):
    # Emitted when a quiz is selected to load its questions in the questions tab
    quiz_selected = Signal(int, str)

    def __init__(self, api_client: APIClient, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.editing_quiz_id: Optional[int] = None
        self._setup_ui()
        self.refresh_quizzes(silent=True)

    def _setup_ui(self):
        layout = QHBoxLayout(self)

        # Left panel: Create / Edit Form
        form_panel = QWidget()
        form_layout = QVBoxLayout(form_panel)

        self.form_header = QLabel("<h2>Manage Quizzes</h2>")
        form_layout.addWidget(self.form_header)

        form_layout.addWidget(QLabel("<b>Quiz Title:</b>"))
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter quiz title (e.g., Python Fundamentals)...")
        form_layout.addWidget(self.title_input)

        form_layout.addWidget(QLabel("<b>Description:</b>"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Optional quiz instructions or details...")
        self.desc_input.setMaximumHeight(90)
        form_layout.addWidget(self.desc_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Create Quiz")
        self.save_btn.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 6px;")
        self.save_btn.clicked.connect(self._on_save_quiz)
        btn_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.clicked.connect(self._clear_form)
        btn_layout.addWidget(self.clear_btn)
        form_layout.addLayout(btn_layout)

        form_layout.addStretch()

        # Right panel: Table of Quizzes & Actions
        table_panel = QWidget()
        table_layout = QVBoxLayout(table_panel)

        table_header_layout = QHBoxLayout()
        table_header_layout.addWidget(QLabel("<h3>Existing Quizzes</h3>"))
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(lambda: self.refresh_quizzes(silent=False))
        table_header_layout.addWidget(refresh_btn)
        table_layout.addLayout(table_header_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Questions", "Created", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_row_double_click)
        table_layout.addWidget(self.table)

        # Action buttons below table
        action_layout = QHBoxLayout()
        self.manage_questions_btn = QPushButton("Manage Questions ➔")
        self.manage_questions_btn.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold; padding: 6px;")
        self.manage_questions_btn.clicked.connect(self._on_manage_questions)
        action_layout.addWidget(self.manage_questions_btn)

        self.edit_btn = QPushButton("✏️ Edit Selected")
        self.edit_btn.setStyleSheet("background-color: #F39C12; color: white; font-weight: bold; padding: 6px;")
        self.edit_btn.clicked.connect(self._on_edit_quiz)
        action_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("🗑️ Delete Selected Quiz")
        self.delete_btn.setStyleSheet("background-color: #E74C3C; color: white; font-weight: bold; padding: 6px;")
        self.delete_btn.clicked.connect(self._on_delete_quiz)
        action_layout.addWidget(self.delete_btn)
        table_layout.addLayout(action_layout)

        layout.addWidget(form_panel, 1)
        layout.addWidget(table_panel, 2)

    def _clear_form(self):
        self.editing_quiz_id = None
        self.title_input.clear()
        self.desc_input.clear()
        self.save_btn.setText("Create Quiz")
        self.save_btn.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold; padding: 6px;")
        self.form_header.setText("<h2>Manage Quizzes</h2>")

    def refresh_quizzes(self, silent: bool = True):
        """Fetch and populate quiz list from backend."""
        try:
            quizzes = self.api_client.list_quizzes()
            self.table.setRowCount(len(quizzes))
            for row_idx, quiz in enumerate(quizzes):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(quiz["id"])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(quiz["title"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(quiz["question_count"])))
                created_display = quiz["created_at"][:19].replace("T", " ")
                self.table.setItem(row_idx, 3, QTableWidgetItem(created_display))
                self.table.setItem(row_idx, 4, QTableWidgetItem("Double-click to open"))
        except Exception as exc:
            self.table.setRowCount(0)
            if not silent:
                QMessageBox.warning(
                    self,
                    "Connection Error",
                    f"Could not connect to backend:\n{exc}\n\nMake sure the backend is running at {self.api_client.base_url}.",
                )

    def _on_edit_quiz(self):
        """Load selected quiz details into the form for editing (FR-03)."""
        quiz_id = self._get_selected_quiz_id()
        if not quiz_id:
            QMessageBox.warning(self, "Selection Required", "Please select a quiz to edit.")
            return

        try:
            quiz = self.api_client.get_quiz(quiz_id)
            self.editing_quiz_id = quiz_id
            self.title_input.setText(quiz["title"])
            self.desc_input.setPlainText(quiz.get("description") or "")
            self.save_btn.setText("💾 Save Quiz Changes")
            self.save_btn.setStyleSheet("background-color: #F39C12; color: white; font-weight: bold; padding: 6px;")
            self.form_header.setText(f"<h2>Edit Quiz #{quiz_id}</h2>")
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Failed to retrieve quiz details: {exc}")

    def _on_save_quiz(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip() or None

        # Pre-add Validation check on client before sending
        if not title:
            QMessageBox.warning(self, "Validation Error (Q06)", "Quiz title cannot be empty or blank!")
            return

        try:
            if self.editing_quiz_id is not None:
                # FR-03: Update existing quiz
                res = self.api_client.update_quiz(self.editing_quiz_id, title=title, description=desc)
                QMessageBox.information(self, "Success", f"Quiz #{res['id']} updated successfully!")
            else:
                # FR-01: Create new quiz
                res = self.api_client.create_quiz(title=title, description=desc)
                QMessageBox.information(self, "Success", f"Quiz '{title}' created successfully with ID #{res['id']}!")

            self._clear_form()
            self.refresh_quizzes(silent=False)
        except Exception as exc:
            err_msg = str(exc)
            # Friendly duplicate warning on 409 Conflict
            if "409" in err_msg or "already exists" in err_msg:
                QMessageBox.warning(
                    self,
                    "Duplicate Quiz Detected (Q06: Search Before Add)",
                    f"A quiz titled '{title}' already exists!\n\n"
                    "Duplicate quiz entries are blocked to protect data integrity.",
                )
            else:
                action = "update" if self.editing_quiz_id else "create"
                QMessageBox.critical(self, "Error", f"Failed to {action} quiz: {exc}")

    def _get_selected_quiz_id(self) -> Optional[int]:
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        row = selected_rows[0].row()
        return int(self.table.item(row, 0).text())

    def _get_selected_quiz_title(self) -> str:
        row = self.table.selectionModel().selectedRows()[0].row()
        return self.table.item(row, 1).text()

    def _on_manage_questions(self):
        quiz_id = self._get_selected_quiz_id()
        if not quiz_id:
            QMessageBox.warning(self, "Selection Required", "Please select a quiz first.")
            return
        title = self._get_selected_quiz_title()
        self.quiz_selected.emit(quiz_id, title)

    def _on_row_double_click(self, row: int, col: int):
        quiz_id = int(self.table.item(row, 0).text())
        title = self.table.item(row, 1).text()
        self.quiz_selected.emit(quiz_id, title)

    def _on_delete_quiz(self):
        """Enforces Q06 Feature 4: Confirmation Dialogs."""
        quiz_id = self._get_selected_quiz_id()
        if not quiz_id:
            QMessageBox.warning(self, "Selection Required", "Please select a quiz to delete.")
            return
        title = self._get_selected_quiz_title()

        # Q06 Feature 4: Confirmation Dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion (Q06 Feature 4)",
            f"Are you sure you want to delete quiz #{quiz_id} ('{title}')?\n\n"
            "This will permanently delete the quiz and all associated questions!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self.api_client.delete_quiz(quiz_id)
                QMessageBox.information(self, "Deleted", "Quiz deleted successfully.")
                if self.editing_quiz_id == quiz_id:
                    self._clear_form()
                self.refresh_quizzes(silent=False)
            except Exception as exc:
                QMessageBox.critical(self, "Error", f"Failed to delete quiz: {exc}")
