from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os

class ImagePopup(QDialog):  #   Ensure it inherits QDialog
    def __init__(self, image_path):
        super().__init__()

        self.setWindowTitle("View Image")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  #   Blocks main window until closed
        self.setStyleSheet("background-color: #222;")

        layout = QVBoxLayout(self)

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            self.label = QLabel("⚠️ Image Not Found")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            screen_size = self.screen().availableGeometry()
            max_width = screen_size.width() * 0.8
            max_height = screen_size.height() * 0.8

            scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.label = QLabel()
            self.label.setPixmap(scaled_pixmap)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.adjustSize()
        self.setMinimumSize(400, 300)
