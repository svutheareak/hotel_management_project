from PyQt6.QtWidgets import QLineEdit

class CustomInput(QLineEdit):
    def __init__(self, placeholder_text="",width=None, height=40, parent=None):
        super().__init__(parent)

        # Set placeholder text
        self.setPlaceholderText(placeholder_text)

        # Apply default styling
        self.setStyleSheet("""
            background-color: 09122C; 
            color: white; 
            border-radius: 5px; 
            padding: 4px; 
            font-size: 14px;
            height : 20px;
        """)

        # Set width and height if provided
        if width:
            self.setFixedWidth(width)
        self.setFixedHeight(height)
