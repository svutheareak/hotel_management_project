import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTreeWidget, QTreeWidgetItem, QHBoxLayout
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class RegistrationForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set the window to be maximized
        self.setWindowFlags(Qt.WindowType.Window)
        self.showMaximized()

        font = QFont("Khmer OS", 11)

        # Set up database connection
        self.conn = sqlite3.connect('school.db')
        self.cursor = self.conn.cursor()

        # Main layout
        main_layout = QVBoxLayout()

        # Form layout
        form_layout = QVBoxLayout()

        # Username
        self.username_label = QLabel("ឈ្មោះអ្នកប្រើប្រាស់:")
        self.username_label.setFont(font)
        self.username_input = QLineEdit()
        self.username_input.setFont(font)

        # Password
        self.password_label = QLabel("លេខសម្ងាត់:")
        self.password_label.setFont(font)
        self.password_input = QLineEdit()
        self.password_input.setFont(font)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Confirm Password
        self.confirm_password_label = QLabel("បញ្ជាក់លេខសម្ងាត់:")
        self.confirm_password_label.setFont(font)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setFont(font)
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Add widgets to form layout
        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_label)
        form_layout.addWidget(self.confirm_password_input)

        # Buttons for CRUD operations
        button_layout = QHBoxLayout()

        self.register_button = QPushButton("ចុះឈ្មោះ")
        self.register_button.setFont(font)
        self.register_button.clicked.connect(self.register)

        self.update_button = QPushButton("កែប្រែ")
        self.update_button.setFont(font)
        self.update_button.clicked.connect(self.update_user)

        self.delete_button = QPushButton("លុប")
        self.delete_button.setFont(font)
        self.delete_button.clicked.connect(self.delete_user)

        self.clear_button = QPushButton("សម្អាត")
        self.clear_button.setFont(font)
        self.clear_button.clicked.connect(self.clear_form)

        # Add buttons to the button layout
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)

        # Add layouts to the form layout
        form_layout.addLayout(button_layout)

        # QTreeWidget for displaying users
        self.user_tree = QTreeWidget()
        self.user_tree.setFont(font)
        self.user_tree.setHeaderLabels(["ID", "ឈ្មោះអ្នកប្រើប្រាស់", "លេខសម្ងាត់"])
        self.user_tree.setColumnWidth(0, 50)
        self.user_tree.setColumnWidth(1, 150)
        self.user_tree.setColumnWidth(2, 150)
        self.user_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Load users into QTreeWidget
        self.load_users()

        # Add layouts to the main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.user_tree)
        self.setLayout(main_layout)

    def load_users(self):
        self.user_tree.clear()
        self.cursor.execute('SELECT id, username, password FROM Tbl_users')
        for row in self.cursor.fetchall():
            masked_password = '*' * len(row[2])  # Mask the password
            QTreeWidgetItem(self.user_tree, [str(row[0]), row[1], masked_password])

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not username or not password or not confirm_password:
            self.show_message("កំហុស", "សូមបំពេញព័ត៌មានអោយពេញលេញ")
            return

        if password != confirm_password:
            self.show_message("កំហុស", "លេខសម្ងាត់មិនដូចគ្នា!")
            return

        try:
            self.cursor.execute('''
                INSERT INTO Tbl_users (username, password)
                VALUES (?, ?)
            ''', (username, password))
            self.conn.commit()
            self.show_message("ជោគជ័យ", "ការចុះឈ្មោះបានសម្រេច!")
            self.load_users()
            self.clear_form()
        except sqlite3.IntegrityError:
            self.show_message("កំហុស", "ឈ្មោះអ្នកប្រើប្រាស់មានរួចហើយ!")

    def update_user(self):
        selected_item = self.user_tree.currentItem()
        if selected_item:
            user_id = selected_item.text(0)
            new_username = self.username_input.text()
            new_password = self.password_input.text()
            confirm_password = self.confirm_password_input.text()

            if new_username and new_password:
                if new_password == confirm_password:
                    confirm = QMessageBox(self)
                    confirm.setWindowTitle("បញ្ជាក់")
                    confirm.setText("តើអ្នកចង់កែប្រែនូវព័ត៌មាននេះមែនទេ?")
                    confirm.setFont(QFont("Khmer OS", 11))
                    confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    response = confirm.exec()

                    if response == QMessageBox.StandardButton.Yes:
                        self.cursor.execute('''
                            UPDATE Tbl_users SET username = ?, password = ? WHERE id = ?
                        ''', (new_username, new_password, user_id))
                        self.conn.commit()
                        self.show_message("ជោគជ័យ", "ការកែប្រែបានជោគជ័យ!")
                        self.load_users()
                        self.clear_form()
                else:
                    self.show_message("កំហុស", "លេខសម្ងាត់មិនដូចគ្នា!")
            else:
                self.show_message("កំហុស", "សូមបំពេញព័ត៌មានអោយពេញលេញ")
        else:
            self.show_message("កំហុស", "សូមជ្រើសរើសអ្នកប្រើប្រាស់មុន!")

    def delete_user(self):
        selected_item = self.user_tree.currentItem()
        if selected_item:
            user_id = selected_item.text(0)

            confirm = QMessageBox(self)
            confirm.setWindowTitle("បញ្ជាក់")
            confirm.setText("តើអ្នកចង់លុបព័ត៌មាននេះមែនទេ?")
            confirm.setFont(QFont("Khmer OS", 11))
            confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            response = confirm.exec()

            if response == QMessageBox.StandardButton.Yes:
                self.cursor.execute('DELETE FROM Tbl_users WHERE id = ?', (user_id,))
                self.conn.commit()
                self.show_message("ជោគជ័យ", "ការលុបបានជោគជ័យ!")
                self.load_users()
                self.clear_form()
        else:
            self.show_message("កំហុស", "សូមជ្រើសរើសអ្នកប្រើប្រាស់មុន!")

    def clear_form(self):
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()

    def on_item_double_clicked(self, item, column):
        self.username_input.setText(item.text(1))
        actual_password = self.get_actual_password(item.text(0))
        self.password_input.setText(actual_password)
        self.confirm_password_input.setText(actual_password)

    def get_actual_password(self, user_id):
        self.cursor.execute('SELECT password FROM Tbl_users WHERE id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else ''

    def show_message(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setFont(QFont("Khmer OS", 11))
        msg.exec()

    def closeEvent(self, event):
        self.conn.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    registration_form = RegistrationForm()
    registration_form.show()
    sys.exit(app.exec())
