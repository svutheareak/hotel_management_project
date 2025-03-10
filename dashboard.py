
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QStackedWidget, QMessageBox, QFrame
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QDateTime, QTimer
import sqlite3

class HotelManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotel Management System")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("icons/paste.png"))
        
        self.initUI()
        self.init_timer()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Top Bar with Date & Time
        self.top_bar_frame = QFrame(self)
        self.top_bar_frame.setStyleSheet("background-color: #BE3144; padding: 0px; height: 10px; border-radius: 10px;")

        self.top_bar_layout = QHBoxLayout(self.top_bar_frame)
        
        self.title_label = QLabel("Hotel Management System", self)
        self.title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")  
        
        self.datetime_label = QLabel("", self)
        self.datetime_label.setStyleSheet("color: white; font-size: 12px;")  
        
        self.top_bar_layout.addWidget(self.title_label)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.datetime_label)
        
        main_layout.addWidget(self.top_bar_frame)

        # 📌 Main Content Layout
        content_layout = QHBoxLayout()
        
        # 📌 Sidebar Navigation
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        self.nav_buttons = []
        
        self.stacked_widget = QStackedWidget()
        self.dashboard_page = self.create_dashboard_page()
        self.room_management_page = self.create_room_management_page()
        self.booking_management_page = self.create_booking_management_page()
        self.payment_billing_page = self.create_payment_billing_page()
        self.employee_management_page = self.create_employee_management_page()
        self.reports_analytics_page = self.create_reports_analytics_page()
        
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.room_management_page)
        self.stacked_widget.addWidget(self.booking_management_page)
        self.stacked_widget.addWidget(self.payment_billing_page)
        self.stacked_widget.addWidget(self.employee_management_page)
        self.stacked_widget.addWidget(self.reports_analytics_page)
        
        nav_items = [
            ("Dashboard", "icons/ic_dashboard.png", self.show_dashboard),
            ("Booking Management", "icons/ic_book.png", self.show_booking_management),
            ("Room Management", "icons/ic_room.png", self.show_room_management),
            ("Payment & Billing", "icons/ic_wallet.png", self.show_payment_billing),
            ("Employee Management", "icons/ic_user.png", self.show_employee_management),
            ("Reports & Analytics", "icons/paste.png", self.show_reports_analytics),
            ("Logout", "icons/ic_logout.png", self.confirm_logout)
        ]
        
        # 🖌️ New Button Style (Compact & Small)
        button_style = """
        QPushButton {
            # background-color: #09122C;
            color: white;
            padding: 2px 8px;  /*   Less spacing */
            text-align: left;
            font-size: 11px;  /*   Smaller font */
            border-radius: 3px;
            height: 28px;  /*   Smaller button height */
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #123456;
        }
        """

        for text, icon, func in nav_items:
            button = QPushButton(text, self)
            button.setIcon(QIcon(icon))
            button.setStyleSheet("padding: 2px 8px; font-size: 11px; height: 28px; min-width: 120px;")
            button.setStyleSheet(button_style)  # Apply compact styling
            button.clicked.connect(func)
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)
        
        sidebar_layout.addStretch()
        content_layout.addLayout(sidebar_layout)
        content_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss a")
        self.datetime_label.setText(current_time)

    def confirm_logout(self):
        reply = QMessageBox.question(self, "Logout", "Do you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()

    ### 📌 Implement Missing Pages ###
    
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Dashboard", self)
        layout.addWidget(title_label)

        room_status_table = QTableWidget(self)
        room_status_table.setColumnCount(2)
        room_status_table.setHorizontalHeaderLabels(["Room Type", "Availability"])
        layout.addWidget(room_status_table)

        page.setLayout(layout)
        return page

    def create_room_management_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Room Management", self)
        layout.addWidget(title_label)
        layout.addWidget(QPushButton("Add Room", self))

        room_table = QTableWidget(self)
        room_table.setColumnCount(3)
        room_table.setHorizontalHeaderLabels(["Room Number", "Capacity", "Price"])
        layout.addWidget(room_table)

        page.setLayout(layout)
        return page

    def create_booking_management_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Booking Management", self)
        layout.addWidget(title_label)
        page.setLayout(layout)
        return page

    def create_payment_billing_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Payment & Billing", self)
        layout.addWidget(title_label)
        page.setLayout(layout)
        return page

    def create_employee_management_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Employee Management", self)
        layout.addWidget(title_label)
        page.setLayout(layout)
        return page

    def create_reports_analytics_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        title_label = QLabel("Reports & Analytics", self)
        layout.addWidget(title_label)
        page.setLayout(layout)
        return page

    ### 📌 Navigation Functions ###
    
    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_page)

    def show_room_management(self):
        self.stacked_widget.setCurrentWidget(self.room_management_page)

    def show_booking_management(self):
        self.stacked_widget.setCurrentWidget(self.booking_management_page)

    def show_payment_billing(self):
        self.stacked_widget.setCurrentWidget(self.payment_billing_page)

    def show_employee_management(self):
        self.stacked_widget.setCurrentWidget(self.employee_management_page)

    def show_reports_analytics(self):
        self.stacked_widget.setCurrentWidget(self.reports_analytics_page)

if __name__ == "__main__":
    app = QApplication([])
    window = HotelManagement()
    app.setWindowIcon(QIcon("icons/paste.png"))
    window.show()
    app.exec()


