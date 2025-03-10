
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QMessageBox, QFrame, QDialog, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QDateTime, QTimer
from dashboardManagement.dashboard_management import DashboardManagement
from loginManagement.login_management import LoginDialog
from paymentManagement.payment_billing import PaymentBilling
from reportManagement.report_management import ReportManagement
from roomManagement.room_management import RoomManagement
from bookingManagement.booking_management import BookingManagement
from guestManagement.guest_management import GuestManagement
from employeeManagement.employee_management import EmployeeManagement
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt

class HotelManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotel Management System")
        self.setGeometry(100, 100, 1200, 700)
        self.setWindowIcon(QIcon("icons/paste.png"))
        plt.ioff() 

        # Login Dialog
        self.login_dialog = LoginDialog()
        if self.login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.user_role = self.login_dialog.role
        else:
            sys.exit()

        self.initUI()
        self.init_timer()
        

    def initUI(self):
        """ Initialize UI Layout """

        if self.layout():
            QWidget().setLayout(self.layout())  # Detach existing layout properly

        main_layout = QVBoxLayout()

        #   Top Bar
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

        #   Sidebar Frame (Fixed Width)
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("background-color: #09122C; border-radius: 5px;")
        self.sidebar.setMinimumWidth(200)  # Prevent sidebar from shrinking too much
        self.sidebar.setMaximumWidth(220)  # Optional: Set max width
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)

        self.nav_buttons = []
        self.stacked_widget = QStackedWidget()

        while self.stacked_widget.count() > 0:
            widget = self.stacked_widget.widget(0)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()  #   Prevent memory leak

        # 📌 Pages
        self.dashboard_page = DashboardManagement()
        self.room_management_page = RoomManagement()
        self.booking_management_page = BookingManagement()
        self.guest_management_page = GuestManagement()
        self.payment_billing_page = PaymentBilling()
        self.employee_management_page = EmployeeManagement()
        self.reports_analytics_page = ReportManagement()

        #   Add Pages Based on Role
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.room_management_page)
        self.stacked_widget.addWidget(self.booking_management_page)
        self.stacked_widget.addWidget(self.guest_management_page)
        self.stacked_widget.addWidget(self.payment_billing_page)
        self.stacked_widget.addWidget(self.reports_analytics_page)

        nav_items = [
            ("Dashboard", "icons/ic_dashboard.png", self.show_dashboard),
            ("Booking Management", "icons/ic_book.png", self.show_booking_management),
            ("Room Management", "icons/ic_room.png", self.show_room_management),
            ("Guest Management", "icons/ic_guest.png", self.show_guest_management),
            ("Payment & Billing", "icons/ic_wallet.png", self.show_payment_billing),
            ("Reports & Analytics", "icons/paste.png", self.show_reports_analytics),
            ("Logout", "icons/ic_logout.png", self.confirm_logout)
        ]

        if self.user_role == "admin":
            self.stacked_widget.addWidget(self.employee_management_page)  #   Add Employee Management
            nav_items.insert(6, ("Employee Management", "icons/ic_user.png", self.show_employee_management))  #   Add to nav

        # 🖌️ Sidebar Button Style
        button_style = """
        QPushButton {
            background-color: #09122C;
            color: white;
            padding: 6px 10px;  
            text-align: left;
            font-size: 12px;  
            border-radius: 5px;
            height: 32px;  
            min-width: 180px;
        }
        QPushButton:hover {
            background-color: #123456;
        }
        """

        for text, icon, func in nav_items:
            button = QPushButton(text, self)
            button.setIcon(QIcon(icon))
            button.setStyleSheet(button_style)
            button.clicked.connect(func)
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_layout.addStretch()
        sidebar_layout.addSpacerItem(QSpacerItem(10, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        #   Add Sidebar & Main Content
        content_layout.addWidget(self.sidebar)  # Sidebar stays fixed
        content_layout.addWidget(self.stacked_widget, 5)  # Main content expands

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        #   Highlight the Dashboard button on first load
        self.highlight_selected_button(self.nav_buttons[0])



    def init_timer(self):
        """ Initialize real-time clock for UI """
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def update_datetime(self):
        """ Update datetime label """
        self.datetime_label.setText(QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss a"))

    def confirm_logout(self):
        """ Handle user logout and reload login form """
        reply = QMessageBox.question(self, "Logout", "Do you want to logout?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.login_dialog = LoginDialog()
            if self.login_dialog.exec() == QDialog.DialogCode.Accepted:
                self.user_role = self.login_dialog.role
                self.reload_ui()
            else:
                sys.exit()

    def reload_ui(self):
        """ Reload the UI when a user logs in again with a new role. """
        for i in reversed(range(self.stacked_widget.count())):
            widget = self.stacked_widget.widget(i)
            self.stacked_widget.removeWidget(widget)
            widget.deleteLater()

        for button in self.nav_buttons:
            button.deleteLater()
        self.nav_buttons.clear()

        self.initUI()

    ### 📌 Navigation Functions ###
    
    def show_dashboard(self):
        self.dashboard_page.load_dashboard_data() 
        self.stacked_widget.setCurrentWidget(self.dashboard_page)
        self.highlight_selected_button(self.nav_buttons[0]) 


    def show_booking_management(self):
        self.booking_management_page.refresh_data()
        self.stacked_widget.setCurrentWidget(self.booking_management_page)
        self.highlight_selected_button(self.nav_buttons[1])

    def show_room_management(self):
        self.room_management_page.refresh_room_list()
        self.stacked_widget.setCurrentWidget(self.room_management_page)
        self.highlight_selected_button(self.nav_buttons[2])

    def show_guest_management(self):
        self.guest_management_page.refresh_guest_list()
        self.stacked_widget.setCurrentWidget(self.guest_management_page)
        self.highlight_selected_button(self.nav_buttons[3])

    def show_payment_billing(self):
        self.payment_billing_page.refresh_data()
        self.stacked_widget.setCurrentWidget(self.payment_billing_page)
        self.highlight_selected_button(self.nav_buttons[4])

    def show_reports_analytics(self):
        self.reports_analytics_page.refresh_report()
        self.stacked_widget.setCurrentWidget(self.reports_analytics_page)
        self.highlight_selected_button(self.nav_buttons[5])

    def show_employee_management(self):
        self.employee_management_page.refresh_data()
        self.stacked_widget.setCurrentWidget(self.employee_management_page)
        self.highlight_selected_button(self.nav_buttons[6])

    def highlight_selected_button(self, selected_button):
        """ Update sidebar button styles to highlight the active button """
        default_style = """
        QPushButton {
            background-color: #09122C;
            color: white;
            padding: 6px 10px;  
            text-align: left;
            font-size: 12px;  
            border-radius: 5px;
            height: 32px;  
            min-width: 180px;
        }
        QPushButton:hover {
            background-color: #123456;
        }
        """

        selected_style = """
        QPushButton {
            background-color: #123456;  /* 🔥 Highlight color */
            color: white;
            font-weight: bold;
            padding: 6px 10px;  
            text-align: left;
            font-size: 12px;  
            border-radius: 5px;
            height: 32px;  
            min-width: 180px;
        }
        """

        # Reset all buttons to default
        for button in self.nav_buttons:
            button.setStyleSheet(default_style)

        # Apply highlight to selected button
        selected_button.setStyleSheet(selected_style)


if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("icons/paste.png"))
    window = HotelManagement()
    window.show()
    app.exec()
