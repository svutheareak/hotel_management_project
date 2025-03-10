

import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from util.dashboard_header import DashboardHeader
from util.dashborad_crad import DashboardCard
from util.custom_table_widget import TableWidget
import matplotlib.pyplot as plt

class DashboardManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Management")
        self.setGeometry(100, 100, 1000, 600)
        self.initUI()
        plt.ioff()  

    def initUI(self):
        """ Initialize Dashboard Layout """

        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        header = DashboardHeader("Hotel Management Dashboard", height=100)
        self.main_layout.addWidget(header)

        # Stats Section (Cards)
        self.stats_grid = QHBoxLayout()
        # self.stats_grid.setSpacing(20)
        self.main_layout.addLayout(self.stats_grid)

        # Cards Data
        self.stats_data = [
            ("Total Bookings", "SELECT COUNT(*) FROM Bookings", "#FF6F61", "icons/ic_calendar.png"),
            ("Total Guests", "SELECT COUNT(*) FROM Guests", "#6A5ACD", "icons/ic_guests.png"),
            ("Total Revenue ($)", "SELECT SUM(amount_paid) FROM Payments", "#2E8B57", "icons/ic_revenue.png"),
            ("Available Rooms", "SELECT COUNT(*) FROM Rooms WHERE status = 'Available'", "#FFA500", "icons/ic_hotel.png")
        ]
        self.load_cards()

        #   Table Section (2 Column Layout)
        self.table_section = QHBoxLayout()
        self.table_section.setSpacing(20)

        #   Create Two Tables
        self.checkin_table = TableWidget("Check-in Today")
        self.checkout_table = TableWidget("Check-out Today")

        self.table_section.addWidget(self.checkin_table)
        self.table_section.addWidget(self.checkout_table)

        self.main_layout.addLayout(self.table_section)
        self.setLayout(self.main_layout)

        #   Load Data into Tables
        self.load_checkin_data()
        self.load_checkout_data()

    ##""" Dynamically generate cards and adjust layout based on screen size """
    def load_cards(self):
        for title, query, color, icon in self.stats_data:
            value = self.fetch_data(query)
            card = DashboardCard(title, value, color, icon)
            self.stats_grid.addWidget(card)

    ##""" Fetch a single value from the database, return 0 if None """
    def fetch_data(self, query):
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        return result[0] if result and result[0] is not None else 0 

    ## Load checkout in Table
    def load_checkin_data(self):
        """ Load check-in data for today with room number instead of room ID """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, COALESCE(r.room_number, 'N/A'), 
                COALESCE(b.check_in_date, 'N/A'), COALESCE(b.check_in_time, 'N/A'), 
                COALESCE(b.check_out_date, 'N/A'), COALESCE(b.check_out_time, 'N/A') 
            FROM BookingDetails b
            LEFT JOIN Rooms r ON b.room_id = r.id
            WHERE b.check_in_date = DATE('now')
        """)
        records = cursor.fetchall()
        conn.close()

        #If empty, avoid crashing
        if not records:  
            records = []

        self.checkin_table.load_data(records)

    ## Load checkout out Table
    def load_checkout_data(self):
        """ Load check-out data for today with room number instead of room ID """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, COALESCE(r.room_number, 'N/A'), 
                COALESCE(b.check_in_date, 'N/A'), COALESCE(b.check_in_time, 'N/A'), 
                COALESCE(b.check_out_date, 'N/A'), COALESCE(b.check_out_time, 'N/A') 
            FROM BookingDetails b
            LEFT JOIN Rooms r ON b.room_id = r.id
            WHERE b.check_out_date = DATE('now')
        """)
        records = cursor.fetchall()
        conn.close()
        
        # If empty, avoid crashing
        if not records:  
            records = []

        self.checkout_table.load_data(records)

        
    def load_dashboard_data(self):
        """ Refresh the dashboard by reloading all cards and table data. """
    
        #Remove existing cards before reloading
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        #Reload Cards and data
        self.load_cards()
        self.load_checkin_data()
        self.load_checkout_data()



