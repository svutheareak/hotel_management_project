from PyQt6.QtWidgets import QFrame, QLabel, QGraphicsOpacityEffect
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import os

class DashboardCard(QFrame):
    def __init__(self, title, value, color, icon_path, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {color}; border-radius: 15px;")
        self.setFixedSize(250, 250)

        #   Title (Centered at the top)
        title_label = QLabel(title, self)
        title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setGeometry(0, 30, 250, 30)

        #   Background Image
        bg_label = QLabel(self)
        
        if not os.path.exists(icon_path):  
            print(f"⚠️ Warning: Image not found at {icon_path}. Using default.")
            icon_path = "icons/default.png"  

        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(" Error: Failed to load image, using empty placeholder.")

        pixmap = pixmap.scaled(130, 130, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        bg_label.setPixmap(pixmap)
        bg_label.setGeometry(20, 110, 130, 130)

        #   Set Opacity Effect
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.7)
        bg_label.setGraphicsEffect(opacity_effect)

        value_label = QLabel(str(value), self)
        value_label.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white; background: transparent; text-align: right")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        value_label.setGeometry(30, 190, 200, 50)  #   Adjusted to overlay the image

