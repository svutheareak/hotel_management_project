from PyQt6.QtWidgets import QLabel

class CustomLabelTitle(QLabel):
    def __init__(self, text, color="white", font_weight="bold", padding="0px", parent=None):
        super().__init__(text, parent)

        self.setStyleSheet(f"""
            color: {color}; 
            font-weight: {font_weight}; 
            padding: {padding}; 
            font-size: 14px;
        """)
