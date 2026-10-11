"""
Main Window for the Teacher Desktop Client.
Organizes Quiz Management and Question Management into clean tabs.
"""

from __future__ import annotations

from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from apps.teacher.api_client import APIClient
from apps.teacher.views.question_view import QuestionView
from apps.teacher.views.quiz_view import QuizView


class TeacherMainWindow(QMainWindow):
    def __init__(self, api_client: APIClient, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.api_client = api_client
        self.setWindowTitle("Online Quiz System — Teacher Management Portal [Q06: Reduce Duplicate Entries]")
        self.resize(1000, 680)

        self._setup_ui()

    def _setup_ui(self):
        self.tabs = QTabWidget()

        # Tab 1: Quizzes
        self.quiz_view = QuizView(self.api_client)
        self.tabs.addTab(self.quiz_view, "📋 Quizzes Management")

        # Tab 2: Questions
        self.question_view = QuestionView(self.api_client)
        self.tabs.addTab(self.question_view, "❓ Questions Management")

        # Connect signal: selecting a quiz in QuizView automatically switches and loads QuestionsView
        self.quiz_view.quiz_selected.connect(self._on_quiz_selected)

        self.setCentralWidget(self.tabs)

        # Status Bar
        status_bar = QStatusBar()
        status_bar.showMessage("Connected to Backend: " + self.api_client.base_url)
        self.setStatusBar(status_bar)

    def _on_quiz_selected(self, quiz_id: int, quiz_title: str):
        self.question_view.set_active_quiz(quiz_id, quiz_title)
        self.tabs.setCurrentIndex(1)  # Switch to Questions tab
