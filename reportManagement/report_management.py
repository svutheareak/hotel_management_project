
from datetime import datetime
import sqlite3
import csv
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QDateEdit, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import Counter

from util.custom_btn import CustomButton

class ReportManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """ Initialize the Report Management UI """
        main_layout = QHBoxLayout(self)

        # 📌 **LEFT: Table View**
        left_section = QVBoxLayout()
        # left_section.setContentsMargins(10, 10, 10, 10)

        report_title = QLabel("Reports & Analytics")
        report_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_section.addWidget(report_title)

        self.report_table = QTableWidget()
        left_section.addWidget(self.report_table)

        # 📌 **RIGHT: Filters, Export & Graph**
        right_section = QVBoxLayout()
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        right_layout = QVBoxLayout(right_frame)

        #   **Report Selection Dropdown**
        right_layout.addWidget(QLabel("Select Report:"))
        self.report_dropdown = QComboBox()
        self.report_dropdown.addItems([
            "Guest Management", "Booking Management", "Payment Management", "Revenue Report"
        ])
        self.report_dropdown.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        self.report_dropdown.currentIndexChanged.connect(self.update_report_columns)
        right_layout.addWidget(self.report_dropdown)

        #   **Date Filters**
        right_layout.addWidget(QLabel("From Date:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        right_layout.addWidget(self.from_date)

        right_layout.addWidget(QLabel("To Date:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        right_layout.addWidget(self.to_date)

        # #   **Generate & Export Buttons**
        self.generate_button = CustomButton("Generate Report", "#4CAF50", "icons/ic_graph.png", height=30)
        self.generate_button.clicked.connect(self.generate_report)
        right_layout.addWidget(self.generate_button)
        
        self.export_button = CustomButton("Export as CSV", "#0277bd", "icons/documents.png", height=30)
        self.export_button.clicked.connect(self.export_to_csv)
        right_layout.addWidget(self.export_button)

        #   **Graph Display**
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(400, 250)
        right_layout.addWidget(self.canvas)

        right_layout.addStretch()
        right_section.addWidget(right_frame)

        # 📌 **Combine Sections**
        main_layout.addLayout(left_section, 6)  # 70%
        main_layout.addLayout(right_section, 4)  # 30%

        self.setLayout(main_layout)
        self.update_report_columns()

    def update_report_columns(self):
        """ Update table columns dynamically based on selected report type and clear previous data """
        report_type = self.report_dropdown.currentText()

        if report_type == "Guest Management":
            headers = ["Guest ID", "Name", "Contact", "Email", "Last Stay"]
        elif report_type == "Booking Management":
            headers = ["Booking ID", "Guest Name", "Room No", "Check-in", "Check-out", "Room Price"]
        elif report_type == "Payment Management":
            headers = ["Payment ID", "Booking ID", "Amount Paid", "Payment Method", "Payment Date"]
        elif report_type == "Revenue Report":
            headers = ["Date", "Booking ID", "Room No", "Room Price", "Total Revenue"]
        else:
            headers = []

        #   Set column headers
        self.report_table.setColumnCount(len(headers))
        self.report_table.setHorizontalHeaderLabels(headers)

        #   Clear any existing table data when switching reports
        self.report_table.setRowCount(0)

    
    def generate_report(self):
        """ Generate the report based on selected filters """
        report_type = self.report_dropdown.currentText()
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")

        if not from_date or not to_date:
            QMessageBox.warning(self, "Input Error", "Please select valid From and To dates.")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        data = []  # Initialize empty data list

        try:
            if report_type == "Guest Management":
                #   FIX: Show all guests including those with upcoming stays
                query = """SELECT G.id, G.name, G.contact, G.email, 
                                COALESCE(MAX(B.check_out_date), 'No Stay') AS last_stay,
                                COUNT(B.id) AS total_stays  --   Show total number of stays
                        FROM Guests G
                        LEFT JOIN Bookings B ON G.id = B.guest_id
                        WHERE (B.check_in_date BETWEEN ? AND ? OR B.check_out_date BETWEEN ? AND ? OR B.id IS NULL)
                        GROUP BY G.id, G.name, G.contact, G.email"""
                
                cursor.execute(query, (from_date, to_date, from_date, to_date))

            elif report_type == "Booking Management":
                query = """SELECT B.id AS booking_id, G.name AS guest_name, R.room_number, 
                                B.check_in_date, B.check_out_date, R.base_price AS room_price
                        FROM Bookings B
                        JOIN Guests G ON B.guest_id = G.id
                        JOIN Rooms R ON B.room_id = R.id
                        WHERE (date(B.check_in_date) BETWEEN ? AND ? OR date(B.check_out_date) BETWEEN ? AND ?)"""
                cursor.execute(query, (from_date, to_date, from_date, to_date))

            elif report_type == "Payment Management":
                query = """SELECT P.id AS payment_id, P.booking_id, P.amount_paid, 
                                P.payment_method, date(P.payment_date)
                        FROM Payments P
                        WHERE date(P.payment_date) BETWEEN ? AND ?"""
                cursor.execute(query, (from_date, to_date))

            elif report_type == "Revenue Report":
                query = """SELECT B.check_in_date AS date, B.id AS booking_id, 
                                R.room_number, R.base_price AS room_price, SUM(P.amount_paid) AS total_amount
                        FROM Bookings B
                        JOIN Payments P ON B.id = P.booking_id
                        JOIN Rooms R ON B.room_id = R.id
                        WHERE date(B.check_in_date) BETWEEN ? AND ?
                        GROUP BY B.check_in_date, B.id, R.room_number"""
                cursor.execute(query, (from_date, to_date))

            else:
                QMessageBox.warning(self, "Invalid Report", "Please select a valid report type.")
                return

            data = cursor.fetchall()
            self.report_table.setRowCount(len(data))

            for row_idx, row_data in enumerate(data):
                for col_idx, item in enumerate(row_data):
                    self.report_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

            #   Ensure the graph updates properly
            self.update_graph(data)
            self.canvas.draw_idle()

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error generating report: {str(e)}")

        finally:
            conn.close()

    def export_to_csv(self):
        """ Export report data to CSV """
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "CSV Files (*.csv)")
        if not file_path:
            return

        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            headers = [self.report_table.horizontalHeaderItem(i).text() for i in range(self.report_table.columnCount())]
            writer.writerow(headers)

            for row in range(self.report_table.rowCount()):
                writer.writerow([self.report_table.item(row, col).text() for col in range(self.report_table.columnCount())])

        QMessageBox.information(self, "Export Success", "Report exported successfully!")

    def update_graph(self, data):
        """ Update the graph visualization based on the selected report data """
        self.ax.clear()  # Clear previous graph

        report_type = self.report_dropdown.currentText()

        if not data:  # No data to plot
            self.ax.set_title("No data available", fontsize=12, fontweight="bold", color="black")
            self.canvas.draw()
            return

        #   Apply common styling (consistent for all graphs)
        self.ax.set_facecolor("#f5f5f5")  # Light gray background
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["left"].set_color("gray")
        self.ax.spines["bottom"].set_color("gray")
        self.ax.grid(True, linestyle="--", linewidth=0.5, color="gray")  # Improved grid

        date_counts = {}

        if report_type == "Revenue Report":
            for row in data:
                date = datetime.strptime(row[0], "%Y-%m-%d").date()
                revenue = float(row[-1])  # Get the total revenue column

                #   Aggregate revenue for the same date
                if date in date_counts:
                    date_counts[date] += revenue
                else:
                    date_counts[date] = revenue

        elif report_type == "Payment Management":
            for row in data:
                date = datetime.strptime(row[-1], "%Y-%m-%d").date()
                amount = float(row[2])

                if date in date_counts:
                    date_counts[date] += amount
                else:
                    date_counts[date] = amount

        elif report_type == "Booking Management":
            dates = [datetime.strptime(row[3], "%Y-%m-%d").date() for row in data]
            date_counts = Counter(dates)  # Count number of bookings per date

        elif report_type == "Guest Management":
            dates = []
            for row in data:
                last_stay = row[-2]
                total_stays = row[-1]

                if isinstance(last_stay, str) and last_stay not in ["No Stay", ""]:
                    try:
                        parsed_date = datetime.strptime(last_stay, "%Y-%m-%d").date()
                        dates.extend([parsed_date] * total_stays)
                    except ValueError:
                        print(f"⚠️ Skipping invalid date: {last_stay}")

            date_counts = Counter(dates) if dates else {}

        else:
            self.ax.set_title("No numerical data available", fontsize=12, fontweight="bold", color="black")
            self.canvas.draw()
            return

        #   Handle empty data after processing
        if not date_counts:
            self.ax.set_title("No data available for this report", fontsize=12, fontweight="bold", color="black")
            self.canvas.draw()
            return

        #   Sort and extract dates & values
        sorted_dates, sorted_counts = zip(*sorted(date_counts.items()))

        #   Set graph colors & labels dynamically
        graph_colors = {
            "Revenue Report": "green",
            "Payment Management": "blue",
            "Booking Management": "orange",
            "Guest Management": "purple",
        }

        self.ax.bar(sorted_dates, sorted_counts, color=graph_colors.get(report_type, "gray"), label=report_type)
        self.ax.set_title(f"{report_type} Trend", fontsize=12, fontweight="bold", color="black")
        self.ax.set_xlabel("Date", fontsize=10, fontweight="bold", color="black")
        self.ax.set_ylabel("Count" if report_type != "Revenue Report" else "Amount ($)", fontsize=10, fontweight="bold", color="black")
        self.ax.legend()

        #   Fix X-axis: Ensure all dates are displayed correctly
        self.ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.ax.tick_params(axis="x", rotation=45, labelsize=8)

        #   Auto-adjust layout to prevent cut-offs
        self.figure.tight_layout()
        self.canvas.draw()


        
    def refresh_report(self):
        """ Refresh the report without changing filters """
        self.generate_report()  
