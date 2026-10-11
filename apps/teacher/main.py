"""
Teacher Desktop Application Entry Point (PySide6).
"""

import sys
from PySide6.QtWidgets import QApplication
from apps.teacher.api_client import APIClient
from apps.teacher.views.main_window import TeacherMainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Consistent modern look across Windows themes

    api_client = APIClient("http://127.0.0.1:8000")
    window = TeacherMainWindow(api_client)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
