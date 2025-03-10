import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QComboBox, QLineEdit, QMessageBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt6.QtGui import QIcon
from util.custom_btn import CustomButton
from util.custom_input import CustomInput
from util.custom_label_title import CustomLabelTitle
from PyQt6.QtCore import Qt

class EmployeeManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_employee_id = None  #   Track selected employee for editing
        self.initUI()

    def initUI(self):
        """ Initialize the Employee Management UI with 70/30 layout """
        main_layout = QHBoxLayout(self)

        # 📌 **LEFT: Employee Table (70%)**
        left_section = QVBoxLayout()
        left_section.setContentsMargins(0, 0, 0, 0)

        table_title = QLabel("Employee List")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_section.addWidget(table_title)

        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(4)  #   Added Actions column
        self.employee_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Actions"])
        left_section.addWidget(self.employee_table)

        # 📌 **RIGHT: Add/Edit Employee Form (30%)**
        right_section = QVBoxLayout()
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        right_layout = QVBoxLayout(right_frame)

        #   Title Layout (Title + Refresh Button aligned Right)
        title_layout = QHBoxLayout()
        
        form_title = QLabel("Add / Edit Employee")
        form_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(form_title)

        title_layout.addStretch()  #   Push refresh button to the right

        #   Refresh Button
        self.refresh_button = QPushButton()
        self.refresh_button.setIcon(QIcon("icons/ic_clear_img.png"))
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.setStyleSheet("background-color: #888; color: white; border-radius: 5px;")
        self.refresh_button.clicked.connect(self.refresh_data)
        title_layout.addWidget(self.refresh_button)

        right_layout.addLayout(title_layout)  #   Add title & refresh button to the layout

        #   Username Input
        self.username_input = CustomInput(placeholder_text="Enter Username", height=30)
        right_layout.addWidget(CustomLabelTitle("Username:"))
        right_layout.addWidget(self.username_input)

        #   Role Dropdown
        right_layout.addWidget(CustomLabelTitle("Role Type:"))
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItem("-- Select Role --")
        self.role_dropdown.addItems(["admin", "user"])
        self.role_dropdown.setCurrentIndex(0) 
        self.role_dropdown.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        right_layout.addWidget(self.role_dropdown)

        #   Password Input
        self.password_input = CustomInput(placeholder_text="Enter Password", height=30)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  #   Hide password input
        right_layout.addWidget(CustomLabelTitle("Password:"))
        right_layout.addWidget(self.password_input)

        #   Add/Update Employee Button
        self.action_button = CustomButton("Add Employee", "#4CAF50", "icons/ic_add.png", height=30)
        self.action_button.clicked.connect(self.handle_employee_action)
        right_layout.addWidget(self.action_button)
        
        right_layout.addStretch()
        right_section.addWidget(right_frame)

        # 📌 **Combine Sections**
        main_layout.addLayout(left_section, 7)  # 70%
        main_layout.addLayout(right_section, 3)  # 30%

        self.setLayout(main_layout)
        self.refresh_data()

    def handle_employee_action(self):
        """ Handle Add or Update based on whether an employee is selected """
        username = self.username_input.text().strip()
        role = self.role_dropdown.currentText().strip()
        password = self.password_input.text().strip()

        if not username or role == "-- Select Role --" or not password:
            QMessageBox.warning(self, "Input Error", "Please enter a username, password, and select a role.")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        try:
            if self.current_employee_id:  #   If editing an existing employee
                cursor.execute(
                    "UPDATE Employees SET username = ?, role = ?, password = ? WHERE id = ?",
                    (username, role, password, self.current_employee_id)
                )
                QMessageBox.information(self, "Success", "Employee updated successfully!")
            else:  #   If adding a new employee
                cursor.execute(
                    "INSERT INTO Employees (username, role, password) VALUES (?, ?, ?)",
                    (username, role, password)
                )
                QMessageBox.information(self, "Success", "Employee added successfully!")

            conn.commit()
            self.refresh_data()
            self.clear_form()

        except sqlite3.IntegrityError as e:
            QMessageBox.warning(self, "Error", f"Failed to save employee: {str(e)}")
        finally:
            conn.close()
            
    def refresh_data(self):
        """ Load all employees from the database and clear the form """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM Employees")  #   Exclude password for security
        employees = cursor.fetchall()
        conn.close()

        self.employee_table.setRowCount(len(employees))
        self.employee_table.setColumnCount(4)
        self.employee_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Actions"])
        self.employee_table.setColumnWidth(3, 100)  #   Set fixed width for Actions column

        for row, (emp_id, username, role) in enumerate(employees):
            self.employee_table.setItem(row, 0, QTableWidgetItem(str(emp_id)))
            self.employee_table.setItem(row, 1, QTableWidgetItem(username))
            self.employee_table.setItem(row, 2, QTableWidgetItem(role))

            #   Action Widget for Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)  #   Remove margins
            action_layout.setSpacing(5)  #   Add slight spacing between buttons

            #   Edit Button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icons/ic_edit.png"))
            edit_button.setFixedSize(30, 30)  #   Same size as room table
            edit_button.setStyleSheet("border: none;")
            edit_button.clicked.connect(lambda _, e_id=emp_id: self.load_employee_for_edit(e_id))
            action_layout.addWidget(edit_button)

            #   Delete Button
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icons/ic_delete.png"))
            delete_button.setFixedSize(30, 30)  #   Consistent size
            delete_button.setStyleSheet("border: none;")
            delete_button.clicked.connect(lambda _, e_id=emp_id: self.delete_employee(e_id))
            action_layout.addWidget(delete_button)

            action_widget.setLayout(action_layout)
            self.employee_table.setCellWidget(row, 3, action_widget)  #   Insert into actions column

        self.clear_form()  #   Ensure form is cleared on refresh

    def load_employee_for_edit(self, emp_id):
        """ Load an employee's data into the form for editing """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, password FROM Employees WHERE id = ?", (emp_id,))
        employee = cursor.fetchone()
        conn.close()

        if not employee:
            QMessageBox.warning(self, "Error", "Employee not found.")
            return

        username, role, password = employee

        #   Set form fields
        self.username_input.setText(username)
        self.role_dropdown.setCurrentText(role)
        self.password_input.setText(password)

        #   Update button text and track employee ID
        self.current_employee_id = emp_id
        self.action_button.setText("Update Employee")
        self.action_button.setStyleSheet("background-color: #FFC107;")  #   Change to yellow

    def delete_employee(self, emp_id):
        """ Delete an employee from the database """
        reply = QMessageBox.question(self, "Delete Employee", "Are you sure you want to delete this employee?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Employees WHERE id = ?", (emp_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Deleted", "Employee deleted successfully.")
            self.refresh_data()

    def clear_form(self):
        """ Reset form inputs and button state """
        self.username_input.clear()
        self.password_input.clear()
        self.role_dropdown.setCurrentIndex(0)
        self.action_button.setText("Add Employee")
        self.action_button.setStyleSheet("background-color: #4CAF50;")
        self.current_employee_id = None  #   Reset employee tracking
