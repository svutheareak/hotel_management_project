from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt
from util.custom_input import CustomInput
from util.custom_btn import CustomButton
import sqlite3
import os


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(700, 400)  # Adjusted to match UI
        self.setStyleSheet("background-color: #333; border-radius: 15px;")  # Rounded corners

        # 🔹 **Main Layout**
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  #   Remove extra padding

        #   **Left Side - Image**
        self.bg_label = QLabel(self)
        self.bg_label.setFixedSize(280, 400)  #   Ensure it matches the form size
        self.load_background_image()  #   Load image
        main_layout.addWidget(self.bg_label, 4)  #   40% Width for Image

        #   **Right Side - Login Form**
        form_frame = QFrame(self)
        form_frame.setStyleSheet("background: #333; border-radius: 10px;")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 🔹 **Title**
        title_label = QLabel("Welcome !")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(title_label)

        # 🔹 **Username Input**
        username_layout = QHBoxLayout()
        username_icon = QLabel()
        username_icon.setPixmap(QPixmap("icons/user.png").scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio))
        username_layout.addWidget(username_icon)

        self.username_input = CustomInput(placeholder_text="@username", height=40)
        self.username_input.setStyleSheet("background-color: black; color: white; border-radius: 5px;")
        username_layout.addWidget(self.username_input)
        form_layout.addLayout(username_layout)

        # 🔹 **Password Input**
        password_layout = QHBoxLayout()
        password_icon = QLabel()
        password_icon.setPixmap(QPixmap("icons/lock.png").scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio))
        password_layout.addWidget(password_icon)

        self.password_input = CustomInput(placeholder_text="Password", height=40)
        self.password_input.setEchoMode(CustomInput.EchoMode.Password)
        self.password_input.setStyleSheet("background-color: black; color: white; border-radius: 5px;")
        password_layout.addWidget(self.password_input)
        form_layout.addLayout(password_layout)

        # 🔹 **Login Button**
        self.login_button = CustomButton("LOGIN", "#6aa84f", "icons/ic_login.png", height=40)  # Green button
        self.login_button.clicked.connect(self.authenticate_user)
        form_layout.addWidget(self.login_button)

        main_layout.addWidget(form_frame, 6)  #   60% Width for Login Form
        self.setLayout(main_layout)

    def load_background_image(self):
        """ Load the background image and fit it properly with opacity 0.8 """
        image_path = "icons/ic_login_img.png"

        #   **Check if the image exists**
        if not os.path.exists(image_path):
            print(f"⚠️ WARNING: Image not found at {image_path}")
            return

        pixmap = QPixmap(image_path)

        #   **Ensure the QPixmap is valid**
        if pixmap.isNull():
            print("ERROR: Failed to load image!")
            return

        #   **Apply Scaling**
        pixmap = pixmap.scaled(
            self.bg_label.width(), self.bg_label.height(),
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        #   **Set the Image**
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setScaledContents(True)  #   Ensure full fit inside QLabel

        #   **Apply Opacity (0.8)**
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)  # **Set opacity to 80%**
        self.bg_label.setGraphicsEffect(opacity_effect)

    def authenticate_user(self):
        """ Validate login credentials """
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM Employees WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.accept()  #   Close login dialog and allow access
            self.role = user[0]  #   Store role to control UI later
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid Username or Password!")
