from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class DashboardHeader(QFrame):
    def __init__(self, title, color="#D81B60", height=80, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {color}; border-radius: 10px;")
        self.setFixedHeight(height)  # Set custom height

        #   Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 20)

        #   Title Label
        title_label = QLabel(title, self)
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(title_label)
        layout.addStretch()  # Pushes text to the left

