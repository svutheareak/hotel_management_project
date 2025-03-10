import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QFrame, QMessageBox, QComboBox, QLineEdit,QListWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from util.custom_btn import CustomButton
from util.custom_input import CustomInput
from util.custom_label_title import CustomLabelTitle
from .generate_invoice import generate_invoice
from paymentManagement.generate_qr_payment import generate_qr_payment
from util.qr_dialog import QRCodeDialog
import time

class PaymentBilling(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Payment Billing Management")
        self.setGeometry(100, 100, 1000, 600)
        self.selected_rooms = {}
        self.initUI()

    def initUI(self):
        """ Initialize UI layout """

        #   Main Layout (Table on Left, Form on Right)
        main_layout = QHBoxLayout(self)

        #   Left Section (Payment Table)
        table_layout = QVBoxLayout()
        table_title = QLabel("Billing Payment")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        #   Search and Filter in the Same Row
        search_filter_layout = QHBoxLayout()

        #   Search Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Guest, Room, or Booking ID")
        self.search_input.textChanged.connect(self.load_payments)
        search_filter_layout.addWidget(self.search_input)

        #   Filter Label (Title)
        filter_label = QLabel("Filter by Status:")
        filter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        search_filter_layout.addWidget(filter_label)

        #   Payment Filter (All, Paid, Unpaid)
        self.payment_filter = QComboBox()
        self.payment_filter.addItems(["All", "Paid", "Unpaid"])
        self.payment_filter.currentIndexChanged.connect(self.load_payments)
        search_filter_layout.addWidget(self.payment_filter)

        #   Add search & filter row to the main table layout
        table_layout.addLayout(search_filter_layout)

        #   Payment Table
        self.payment_table = QTableWidget()
        self.payment_table.setColumnCount(10)  #   Add extra column for Room Price
        self.payment_table.setHorizontalHeaderLabels([
            "", "Booking ID", "Guest", "Room", "Room Price", "Check-in", "Check-out", "Remaining Balance", "Payment Status", "Actions"
        ])
        self.payment_table.cellClicked.connect(self.update_selected_rooms)
        table_layout.addWidget(self.payment_table)

        #   Right Section (Add Payment Form)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)

        title_label = QLabel("Add Payment")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        form_layout.addWidget(title_label)
        
        


        #   List Widget to Show Selected Rooms
        self.selected_rooms_list = QListWidget()
        self.selected_rooms_list.setStyleSheet("background-color: #444; color: white; border-radius: 5px; padding: 5px;")
        form_layout.addWidget(QLabel("Selected Rooms:"))
        form_layout.addWidget(self.selected_rooms_list)

        #   Label for Total Price
        self.total_price_label = QLabel("Total Price: $0.00")
        self.total_price_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        form_layout.addWidget(self.total_price_label)

        self.amount_paid_input = CustomInput(placeholder_text="Enter Amount", height=30)
        form_layout.addWidget(CustomLabelTitle("Amount Paid:"))
        form_layout.addWidget(self.amount_paid_input)

        self.payment_method_input = QComboBox()
        self.payment_method_input.addItems(["Cash", "KHQR"])
        form_layout.addWidget(CustomLabelTitle("Payment Method:"))
        form_layout.addWidget(self.payment_method_input)

        #   Pay All Button
        self.pay_all_button = CustomButton("Pay", "#ff9800", "icons/ic_wallet.png", height=30)
        self.pay_all_button.clicked.connect(self.pay_all_bookings)
        form_layout.addWidget(self.pay_all_button)

        #   Print Button
        self.print_button = CustomButton("🖨️ Print", "#4CAF50", "icons/ic_print.png", height=30)
        self.print_button.clicked.connect(self.print_selected_bookings)
        form_layout.addWidget(self.print_button)

        form_layout.addStretch()

        #   Combine Layouts
        main_layout.addLayout(table_layout, 7)
        main_layout.addWidget(form_frame, 3)

        self.setLayout(main_layout)
        self.load_payments()

    def print_selected_bookings(self):
        """ Print selected bookings and generate PDF invoice """
        if not self.selected_rooms:
            QMessageBox.warning(self, "Error", "Please select at least one booking to print!")
            return

        # Generate PDF invoice
        generate_invoice(self.selected_rooms)
    
    def update_selected_rooms(self, row, column):
        """ Update selected rooms list and total price when checkboxes are toggled """
        if column == 0:  # Checkbox column (Selection Checkbox)
            item = self.payment_table.item(row, column)
            booking_id = self.payment_table.item(row, 1).text()  # Booking ID
            guest_name = self.payment_table.item(row, 2).text().strip()  # Guest Name
            room_number = self.payment_table.item(row, 3).text().strip()  # Room Number

            #   Fetch `room_type` and `room_price` from Database using `room_number`
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            cursor.execute("SELECT room_type, base_price FROM Rooms WHERE TRIM(room_number) = ?", (room_number,))
            room_data = cursor.fetchone()
            conn.close()

            #   Ensure room_type and room_price are assigned properly
            room_type = room_data[0].strip() if room_data and room_data[0] else "Unknown"
            room_price = float(room_data[1]) if room_data and room_data[1] else 0.0  #   Store Correct Room Price

            try:
                check_in_date = self.payment_table.item(row, 5).text()
                in_time = self.payment_table.item(row, 6).text()
                check_out_date = self.payment_table.item(row, 7).text()
                out_time = self.payment_table.item(row, 8).text()
                remaining_balance = float(self.payment_table.item(row, 9).text().replace("$", ""))  
                payment_status = self.payment_table.item(row, 10).text()
            except (AttributeError, ValueError):
                return  

            if not hasattr(self, 'selected_rooms'):  #   Ensure the variable exists
                self.selected_rooms = {}

            if item.checkState() == Qt.CheckState.Checked:
                self.selected_rooms[booking_id] = {
                    "guest": guest_name,  
                    "room": room_number,
                    "room_type": room_type, 
                    "room_price": room_price, 
                    "remaining": remaining_balance,  
                    "check_in": check_in_date,
                    "check_in_time": in_time,
                    "check_out": check_out_date,
                    "check_out_time": out_time,
                    "status": payment_status
                }
            else:
                self.selected_rooms.pop(booking_id, None) 

            self.update_selected_rooms_display()




    def load_payments(self):
        """ Load payments from the database into the table with search functionality and filter options """
        
         #   Clear selected rooms before filtering
        self.selected_rooms.clear()
        self.selected_rooms_list.clear()
        self.total_price_label.setText("Total Price: $0.00")
        self.amount_paid_input.clear()


        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        search_text = self.search_input.text().strip()
        selected_filter = self.payment_filter.currentText()  #   Get Selected Filter

        #   Base SQL query
        sql_query = """
            SELECT b.id, g.name, r.room_number, b.check_in_date, 
                IFNULL(b.check_in_time, '12:00') AS check_in_time,  
                b.check_out_date, 
                IFNULL(b.check_out_time, '10:00') AS check_out_time, 
                r.base_price, 
                (bd.calculated_price - IFNULL((SELECT SUM(amount_paid) FROM Payments WHERE booking_id = b.id), 0)) AS remaining_balance,
                b.payment_status
            FROM Bookings b
            JOIN Guests g ON b.guest_id = g.id
            JOIN Rooms r ON b.room_id = r.id
            JOIN BookingDetails bd ON b.id = bd.booking_id
            WHERE b.check_in_date >= DATE('now', '-30 days')
        """
        
        params = []

        #   Apply Payment Status Filter
        if selected_filter == "Paid":
            sql_query += " AND b.payment_status = 'PAID'"
        elif selected_filter == "Unpaid":
            sql_query += " AND b.payment_status IN ('PENDING', 'HALF PAID')"

        #   Apply Search Filter
        if search_text:
            sql_query += " AND (g.name LIKE ? OR r.room_number LIKE ? OR b.id LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"])

        sql_query += " ORDER BY b.check_in_date DESC"

        #   Execute Query
        cursor.execute(sql_query, params)
        payments = cursor.fetchall()
        conn.close()

        #   Populate the Table
        self.payment_table.clearContents()
        self.payment_table.setRowCount(len(payments))
        self.payment_table.setColumnCount(11)  #   Remove Actions column
        self.payment_table.setHorizontalHeaderLabels([
            "", "Booking ID", "Guest", "Room", "Room Price", "Check-in", "In Time", 
            "Check-out", "Out Time", "Remaining", "Status"
        ])


        #   Set Column Widths for Better UI
        column_widths = [30, 75, 120, 60, 90, 100, 60, 100, 70, 110, 110]  
        for i, width in enumerate(column_widths):
            self.payment_table.setColumnWidth(i, width)

        #   Loop Through Data and Populate Table
        for row_idx, (booking_id, guest, room, check_in, check_in_time, check_out, check_out_time, room_price, remaining_balance, payment_status) in enumerate(payments):
            check_box = QTableWidgetItem()
            check_box.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            check_box.setCheckState(Qt.CheckState.Unchecked)  #   Ensure Unchecked
            self.payment_table.setItem(row_idx, 0, check_box)

            self.payment_table.setItem(row_idx, 1, QTableWidgetItem(str(booking_id)))  # Booking ID
            self.payment_table.setItem(row_idx, 2, QTableWidgetItem(guest))  # Guest Name
            self.payment_table.setItem(row_idx, 3, QTableWidgetItem(str(room)))  # Room Number
            self.payment_table.setItem(row_idx, 4, QTableWidgetItem(f"${room_price:.2f}"))  #   Room Price
            self.payment_table.setItem(row_idx, 5, QTableWidgetItem(check_in))  # Check-in Date
            self.payment_table.setItem(row_idx, 6, QTableWidgetItem(check_in_time))  #   Check-in Time
            self.payment_table.setItem(row_idx, 7, QTableWidgetItem(check_out))  # Check-out Date
            self.payment_table.setItem(row_idx, 8, QTableWidgetItem(check_out_time))  #   Check-out Time
            self.payment_table.setItem(row_idx, 9, QTableWidgetItem(f"${remaining_balance:.2f}"))  #   Remaining Balance
            self.payment_table.setItem(row_idx, 10, QTableWidgetItem(payment_status))  # Payment Status



    def update_selected_rooms(self, row, column):
        """ Update selected rooms list and total price when checkboxes are toggled """
        if column == 0:  # Checkbox column (Selection Checkbox)
            item = self.payment_table.item(row, column)
            booking_id = self.payment_table.item(row, 1).text()  # Booking ID
            guest_name = self.payment_table.item(row, 2).text().strip()  # Guest Name
            room_number = self.payment_table.item(row, 3).text().strip()  # Room Number

            try:
                room_price = float(self.payment_table.item(row, 4).text().replace("$", ""))
                check_in_date = self.payment_table.item(row, 5).text()
                in_time = self.payment_table.item(row, 6).text()
                check_out_date = self.payment_table.item(row, 7).text()
                out_time = self.payment_table.item(row, 8).text()
                remaining_balance = float(self.payment_table.item(row, 9).text().replace("$", ""))  #   Get the correct remaining balance
                payment_status = self.payment_table.item(row, 10).text()
            except (AttributeError, ValueError):
                return  #   Prevent crashes due to missing or invalid data

            if not hasattr(self, 'selected_rooms'):  #   Ensure the variable exists
                self.selected_rooms = {}

            if item.checkState() == Qt.CheckState.Checked:
                self.selected_rooms[booking_id] = {
                    "guest": guest_name,  
                    "room": room_number,
                    "price": remaining_balance,  #   Store the correct remaining balance instead of room price
                    "check_in": check_in_date,
                    "check_in_time": in_time,
                    "check_out": check_out_date,
                    "check_out_time": out_time,
                    "remaining": remaining_balance,  #   Ensure this is used correctly
                    "status": payment_status
                }
            else:
                self.selected_rooms.pop(booking_id, None)  #   Remove if unchecked

            self.update_selected_rooms_display()



    def update_selected_rooms_display(self):
        """ Update the UI to show selected rooms and total price dynamically """
        self.selected_rooms_list.clear()
        total_price = sum(room["price"] for room in self.selected_rooms.values())

        for booking_id, data in self.selected_rooms.items():
            self.selected_rooms_list.addItem(f"Room {data['room']} - Remaining: ${data['price']:.2f}")

        self.total_price_label.setText(f"Total Price: ${total_price:.2f}")  #   Shows correct total price

    
    def pay_all_bookings(self):
        """ Process payments for multiple selected bookings and distribute amounts correctly """
        selected_booking_ids = []

        #   Get Selected Bookings
        for row in range(self.payment_table.rowCount()):
            check_box = self.payment_table.item(row, 0)
            if check_box and check_box.checkState() == Qt.CheckState.Checked:
                booking_id = int(self.payment_table.item(row, 1).text())
                selected_booking_ids.append(booking_id)

        if not selected_booking_ids:
            QMessageBox.warning(self, "Error", "Please select at least one booking to pay!")
            return

        #   Validate Amount Input
        amount_paid_text = self.amount_paid_input.text().strip()
        if not amount_paid_text:
            QMessageBox.warning(self, "Error", "Please enter a valid amount.")
            return

        try:
            total_amount_paid = float(amount_paid_text)
            if total_amount_paid <= 0:
                raise ValueError("Amount must be greater than zero")
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid payment amount!")
            return

        payment_method = self.payment_method_input.currentText()


        if payment_method == "KHQR":
            currency = "USD"

            timestamp = int(time.time())

            #   Prefix with "py" to make it unique
            trans_order_no = f"py{timestamp}"
            
            qr_image_data = generate_qr_payment(total_amount_paid, currency, trans_order_no)

            if qr_image_data:
                order_id = trans_order_no  #   Replace with actual order ID from response
                dialog = QRCodeDialog(qr_image_data, order_id, self.refresh_data)  #   Pass `update_ui`
                dialog.exec()  #   Show QR Code Dialog
            else:
                QMessageBox.warning(self, "Error", "Failed to generate QR Code!")

            return  #   Stop further execution after QR generation

        
        #   Fetch Remaining Balances for Selected Bookings
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        booking_details = []
        total_remaining_balance = 0.0

        for booking_id in selected_booking_ids:
            cursor.execute("""
                SELECT calculated_price, 
                    (calculated_price - IFNULL((SELECT SUM(amount_paid) FROM Payments WHERE booking_id = ?), 0)) AS remaining_balance
                FROM BookingDetails
                WHERE booking_id = ?
            """, (booking_id, booking_id))

            result = cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Error", f"Booking ID {booking_id} not found!")
                conn.close()
                return

            calculated_price, remaining_balance = result
            booking_details.append((booking_id, calculated_price, remaining_balance))
            total_remaining_balance += remaining_balance

        #   Prevent Overpayment
        if total_amount_paid > total_remaining_balance:
            QMessageBox.warning(self, "Error", "Payment exceeds total remaining balance for selected bookings!")
            conn.close()
            return

        #   Distribute Payments Proportionally
        remaining_amount = total_amount_paid
        for booking_id, calculated_price, remaining_balance in booking_details:
            if remaining_amount <= 0:
                break

            #   Calculate how much to pay for this booking
            payment_amount = min(remaining_balance, remaining_amount)

            #   Insert Payment Record
            cursor.execute("""
                INSERT INTO Payments (booking_id, amount_paid, payment_method, payment_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (booking_id, payment_amount, payment_method))

            #   Calculate New Remaining Balance & Status
            new_remaining_balance = max(remaining_balance - payment_amount, 0)  
            new_status = "PAID" if new_remaining_balance == 0 else "HALF PAID"

            #   Update Payment Status in `BookingDetails`
            cursor.execute("""
                UPDATE BookingDetails
                SET payment_status = ?
                WHERE booking_id = ?
            """, (new_status, booking_id))

            #   Update Payment Status in `Bookings`
            cursor.execute("""
                UPDATE Bookings
                SET payment_status = ?
                WHERE id = ?
            """, (new_status, booking_id))

            #   Reduce Remaining Amount
            remaining_amount -= payment_amount

        conn.commit()  #   Commit all changes
        conn.close()

        QMessageBox.information(self, "Success", "Payments processed successfully!")
        self.refresh_data()  #   Refresh UI after payment



    def refresh_data(self):
        """ Refresh the payment table and reset selected rooms """
        self.load_payments()  #   Reload payments from the database
        self.selected_rooms.clear()  #   Clear selected room data
        self.selected_rooms_list.clear()  #   Clear the UI list
        self.total_price_label.setText("Total Price: $0.00")  #   Reset total price
        self.amount_paid_input.clear()  #   Clear payment input field
