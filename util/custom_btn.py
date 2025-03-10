from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class CustomButton(QPushButton):
    def __init__(self, text, color, icon_path=None, width=None, height=40, parent=None):
        super().__init__(f"\u00A0 {text}", parent)  # Add a space before text to push it from the icon

        # Apply background color and text styling
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                border-radius: 5px; 
                font-size: 14px;
                padding: 6px 12px;  /* Adds better horizontal padding */
                text-align: center; /* Ensures text alignment looks good */
            }}
        """)

        # Set button size dynamically
        if width:  # If width is provided, use it
            self.setFixedSize(QSize(width, height))
        else:  # If no width is given, expand with parent
            self.setMinimumHeight(height)  # Keep height fixed, but allow width to be flexible

        # Add icon if provided
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(16, 16))  # Adjust icon size
