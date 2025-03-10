
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QDateEdit, QTimeEdit,QFrame
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QDate, QTime, QTimer
import sqlite3

from util.custom_btn import CustomButton
from util.custom_input import CustomInput
from PyQt6.QtGui import QPixmap
import os

class BookingManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """ Create the Booking Management UI layout """

        #   Main Layout (Table on Left, Form on Right)
        main_layout = QHBoxLayout(self)

        #   Left Section (Booking List Table)
        table_layout = QVBoxLayout()
        table_title = QLabel("Booking List")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.booking_table = QTableWidget()
        self.booking_table.setColumnCount(6)
        self.booking_table.setHorizontalHeaderLabels(["ID", "Guest", "Room", "Check-in", "Check-out", "Status"])
        table_layout.addWidget(self.booking_table)

        #   Right Section (Add/Edit Booking Form)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)

        #   Title & Action Buttons
        title_layout = QHBoxLayout()
        title_label = QLabel("Add / Edit Booking")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)

        self.clear_button = QPushButton()
        self.clear_button.setIcon(QIcon("icons/ic_clear_img.png"))
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.setStyleSheet("background-color: #888; color: white; border-radius: 5px;")
        self.clear_button.clicked.connect(self.clear_form)
        title_layout.addWidget(self.clear_button)

        form_layout.addLayout(title_layout)
        
        #   Price Type Selection
        price_type_label = QLabel("Select Price Type:")
        price_type_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(price_type_label)

        self.price_type_dropdown = QComboBox()
        self.price_type_dropdown.addItem("-- Select Price Type --")  # Default empty selection
        self.price_type_dropdown.addItems(["Normal", "Low Season", "High Season", "3 Hour"])
        self.price_type_dropdown.currentIndexChanged.connect(self.toggle_price_input)
        self.price_type_dropdown.setCurrentIndex(0)
        self.price_type_dropdown.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.price_type_dropdown)

        #   Custom Price Input (Hidden by Default)
        self.custom_price_label = QLabel("Custom Price")
        self.custom_price_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        self.custom_price_label.setVisible(False)
        form_layout.addWidget(self.custom_price_label)

        self.custom_price_input = CustomInput(placeholder_text="Enter Custom Price", height=30)
        self.custom_price_input.setVisible(False)
        form_layout.addWidget(self.custom_price_input)
        
        
       
        

        #   Move Check-in and Check-out Fields to the Top
        check_in_date_label = QLabel("Check-in Date:")
        check_in_date_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(check_in_date_label)

        self.check_in_date = QDateEdit()
        self.check_in_date.setCalendarPopup(True)
        self.check_in_date.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        self.check_in_date.setDate(QDate.currentDate())
        form_layout.addWidget(self.check_in_date)

        self.check_in_time_label = QLabel("Check-in Time:")
        self.check_in_time_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(self.check_in_time_label)

        self.check_in_time = QTimeEdit()
        self.check_in_time.setDisplayFormat("HH:mm")
        self.check_in_time.setTime(QTime(12, 0))  # Default to noon
        self.check_in_time.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.check_in_time)

        check_out_date_label = QLabel("Check-out Date:")
        check_out_date_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(check_out_date_label)

        self.check_out_date = QDateEdit()
        self.check_out_date.setCalendarPopup(True)
        self.check_out_date.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        self.check_out_date.setDate(QDate.currentDate().addDays(1))
        form_layout.addWidget(self.check_out_date)

        self.check_out_time_label = QLabel("Check-out Time:")
        self.check_out_time_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(self.check_out_time_label)

        self.check_out_time = QTimeEdit()
        self.check_out_time.setDisplayFormat("HH:mm")
        self.check_out_time.setTime(QTime(10, 0))  # Default to 10 AM
        self.check_out_time.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.check_out_time)
        
        #   Room Selection
        room_label = QLabel("Room:")
        room_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(room_label)

        self.room_dropdown = QComboBox()
        self.load_available_rooms()
        self.room_dropdown.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.room_dropdown)

        #   Guest Selection
        guest_label = QLabel("Guest:")
        guest_label.setStyleSheet("color: white; font-weight: bold; padding: 0px") 
        form_layout.addWidget(guest_label)

        self.guest_dropdown = QComboBox()
        self.load_guests()
        self.guest_dropdown.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.guest_dropdown)

       

        # Connect signals to dynamically update available rooms
        self.check_in_date.dateChanged.connect(self.filter_available_rooms)
        self.check_out_date.dateChanged.connect(self.filter_available_rooms)
        self.check_in_time.timeChanged.connect(self.filter_available_rooms)
        self.check_out_time.timeChanged.connect(self.filter_available_rooms)
        self.price_type_dropdown.currentIndexChanged.connect(self.filter_available_rooms)


        #   Add Booking & Cancel Booking Buttons
        self.add_booking_button = CustomButton("Add Booking", "#017f28", "icons/ic_add.png", height=30)
        self.add_booking_button.clicked.connect(self.add_booking)
        form_layout.addWidget(self.add_booking_button)

        self.cancel_booking_button = CustomButton("Cancel Booking", "red", "icons/ic_cancel.png", height=30)
        self.cancel_booking_button.clicked.connect(self.cancel_booking)
        form_layout.addWidget(self.cancel_booking_button)

        form_layout.addStretch()

        #   Combine Layouts (70% Table, 30% Form)
        main_layout.addLayout(table_layout, 7)
        main_layout.addWidget(form_frame, 3)

        self.setLayout(main_layout)
        self.load_bookings()


    def refresh_data(self):
        """ Refresh the guest and room dropdown lists """
        self.load_guests()
        self.load_available_rooms()
        self.reset_form()
        
    def clear_form(self):
        """ Clears the booking form fields """
        self.guest_dropdown.setCurrentIndex(0)
        self.room_dropdown.setCurrentIndex(0)
        self.check_in_date.setDate(QDate.currentDate())
        self.check_out_date.setDate(QDate.currentDate().addDays(1))
        self.reset_form()

    def load_bookings(self):
        """ Load all bookings into the table with Edit & Delete buttons """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, g.name, r.room_number, 
                b.check_in_date, 
                IFNULL(b.check_in_time, '12:00'),  -- Ensure empty times show as "-"
                b.check_out_date, 
                IFNULL(b.check_out_time, '10:00'), 
                IFNULL(bd.calculated_price, 0), 
                b.price_type, 
                b.status
            FROM Bookings b
            JOIN Guests g ON b.guest_id = g.id
            JOIN Rooms r ON b.room_id = r.id
            LEFT JOIN BookingDetails bd ON b.id = bd.booking_id
            ORDER BY b.check_in_date DESC
        """)




        bookings = cursor.fetchall()
        conn.close()

        self.booking_table.setRowCount(len(bookings))
        self.booking_table.setColumnCount(11)  # Ensure 11 columns match headers
        self.booking_table.setHorizontalHeaderLabels([
            "ID", "Guest", "Room", "Check-in", "In Time", "Check-out", "Out Time", "Price", "Price Type", "Status", "Actions"
        ])

        #   Set Column Widths
        column_widths = [50, 120, 50, 100, 70, 100, 70, 100, 100, 100, 140]
        for i, width in enumerate(column_widths):
            self.booking_table.setColumnWidth(i, width)

        #   Auto-resize remaining columns
        self.booking_table.horizontalHeader().setStretchLastSection(True)

        for row, (booking_id, guest, room, check_in, check_in_time, check_out, check_out_time, total_price, price_type, status) in enumerate(bookings):
            self.booking_table.setItem(row, 0, QTableWidgetItem(str(booking_id)))
            self.booking_table.setItem(row, 1, QTableWidgetItem(guest))
            self.booking_table.setItem(row, 2, QTableWidgetItem(str(room)))
            self.booking_table.setItem(row, 3, QTableWidgetItem(check_in))
            self.booking_table.setItem(row, 4, QTableWidgetItem(check_in_time))  #   Fixed "In Time"
            self.booking_table.setItem(row, 5, QTableWidgetItem(check_out))
            self.booking_table.setItem(row, 6, QTableWidgetItem(check_out_time))  #   Fixed "Out Time"
            self.booking_table.setItem(row, 7, QTableWidgetItem(f"${total_price:.2f}"))  #   Fixed Price
            self.booking_table.setItem(row, 8, QTableWidgetItem(price_type))
            self.booking_table.setItem(row, 9, QTableWidgetItem(status))

            #   Add Action Buttons (Edit & Delete)
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icons/ic_edit.png"))
            edit_button.setFixedSize(30, 30)
            edit_button.setStyleSheet("border: none;")
            edit_button.clicked.connect(lambda _, b_id=booking_id: self.edit_booking(b_id))
            action_layout.addWidget(edit_button)

            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icons/ic_delete.png"))
            delete_button.setFixedSize(30, 30)
            delete_button.setStyleSheet("border: none;")
            delete_button.clicked.connect(lambda _, b_id=booking_id: self.delete_booking(b_id))
            action_layout.addWidget(delete_button)
            
            # 🔥 **Check In Button**
            check_in_button = QPushButton()
            check_in_button.setIcon(QIcon("icons/ic_in.png"))  # Use an appropriate icon
            check_in_button.setFixedSize(30, 30)
            check_in_button.setStyleSheet("border: none;")
            check_in_button.clicked.connect(lambda _, b_id=booking_id: self.confirm_checkin(b_id))
            # check_in_button.setEnabled(status == "CHECKED-OUT")
            action_layout.addWidget(check_in_button)
            
            #   Check-Out Button (Only enable if Checked-In)
            check_out_button = QPushButton()
            check_out_button.setIcon(QIcon("icons/ic_out.png"))  # Use your own icon
            check_out_button.setFixedSize(30, 30)
            check_out_button.setStyleSheet("border: none; color: white; border-radius: 5px;")
            check_out_button.clicked.connect(lambda _, b_id=booking_id: self.confirm_checkout(b_id))
            check_out_button.setEnabled(status == "CHECKED-IN")  #   Disable if not checked in
            action_layout.addWidget(check_out_button)
            
             
            action_widget.setLayout(action_layout)
            self.booking_table.setCellWidget(row, 10, action_widget)  #   Action Column
            
    def confirm_checkin(self, booking_id):
        """ Show confirmation popup before check-in with custom icon """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        # 🔍 Fetch booking details
        cursor.execute("""
            SELECT guest_id, room_id, check_in_date, check_out_date, status 
            FROM Bookings WHERE id=?
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            QMessageBox.warning(self, "Error", "Booking not found!")
            return

        guest_id, room_id, check_in_date, check_out_date, current_status = booking

        if current_status == "CHECKED-IN":
            QMessageBox.warning(self, "Error", "This guest is already checked in!")
            return

        #   Create custom QMessageBox with Icon
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Check-In")
        msg_box.setText(
            f"<b>Are you sure you want to check in this guest?</b><br><br>"
            f"👤 <b>Guest ID:</b> {guest_id}<br>"
            "<br>---------------------------------------<br>"
            f"🏨 <b>Room ID:</b> {room_id}<br>"
            "<br>---------------------------------------<br>"
            f"📅 <b>Check-in Date:</b> {check_in_date}<br>"
            "<br>---------------------------------------<br>"
            f"📅 <b>Check-out Date:</b> {check_out_date}"
        )
        msg_box.setIconPixmap(QPixmap("icons/ic_question.png").scaled(64, 64))  

        msg_box.setStyleSheet("QLabel{color: white;}")  
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        confirm = msg_box.exec()

        if confirm == QMessageBox.StandardButton.Yes:
            cursor.execute("UPDATE Bookings SET status = 'CHECKED-IN' WHERE id = ?", (booking_id,))
            cursor.execute("""
                INSERT INTO GuestHistory (guest_id, room_id, check_in_date, check_out_date, payment_status)
                VALUES (?, ?, ?, ?, 'PENDING')
            """, (guest_id, room_id, check_in_date, check_out_date))

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Guest has been checked in successfully!")
            self.load_bookings()  # 🔄 Refresh UI
            
    def confirm_checkout(self, booking_id):
        """ Show confirmation popup before check-out with custom icon """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        # 🔍 Fetch booking details
        cursor.execute("""
            SELECT guest_id, room_id, check_out_date, status 
            FROM Bookings WHERE id=?
        """, (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            QMessageBox.warning(self, "Error", "Booking not found!")
            return

        guest_id, room_id, check_out_date, current_status = booking

        if current_status == "CHECKED-OUT":
            QMessageBox.warning(self, "Error", f"Guest already checked out on {check_out_date}!")
            return

        #   Create custom QMessageBox with Icon
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Check-Out")
        msg_box.setText(
            f"<b>Are you sure you want to check out this guest?</b><br><br>"
            f"👤 <b>Guest ID:</b> {guest_id}<br>"
            "<br>---------------------------------------<br>"
            f"🏨 <b>Room ID:</b> {room_id}<br>"
            "<br>---------------------------------------<br>"
            f"📅 <b>Check-out Date:</b> {check_out_date}"
        )
        msg_box.setIconPixmap(QPixmap("icons/ic_question.png").scaled(64, 64))  
        msg_box.setStyleSheet("QLabel{color: white;}") 
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        confirm = msg_box.exec()

        if confirm == QMessageBox.StandardButton.Yes:
            cursor.execute("UPDATE Bookings SET status = 'CHECKED-OUT' WHERE id = ?", (booking_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Guest has been checked out successfully!")
            self.load_bookings() 


    def edit_booking(self, booking_id):
        """ Load booking details into the form for editing """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.name, r.id, r.room_number, b.check_in_date, b.check_out_date, 
                b.check_in_time, b.check_out_time, bd.calculated_price, b.price_type
            FROM Bookings b
            JOIN Guests g ON b.guest_id = g.id
            JOIN Rooms r ON b.room_id = r.id
            LEFT JOIN BookingDetails bd ON b.id = bd.booking_id
            WHERE b.id=?
        """, (booking_id,))
        booking = cursor.fetchone()
        conn.close()

        if not booking:
            QMessageBox.warning(self, "Error", "Booking not found!")
            return

        guest_name, room_id, room_number, check_in, check_out, check_in_time, check_out_time, total_price, price_type = booking

        #   Load Guest
        guest_index = self.guest_dropdown.findText(guest_name)
        if guest_index != -1:
            self.guest_dropdown.setCurrentIndex(guest_index)
        self.load_available_rooms(selected_room=room_id)
        for i in range(self.room_dropdown.count()):
            print(f"  - Index {i}: {self.room_dropdown.itemText(i)} (Data: {self.room_dropdown.itemData(i)})")


        #   Set Check-in/Check-out Dates
        self.check_in_date.setDate(QDate.fromString(check_in, "yyyy-MM-dd"))
        self.check_out_date.setDate(QDate.fromString(check_out, "yyyy-MM-dd"))

        #   Load Price Type
        price_type_index = self.price_type_dropdown.findText(price_type)
        if price_type_index != -1:
            self.price_type_dropdown.setCurrentIndex(price_type_index)
        #   Load Check-in and Check-out Time
        if price_type == "3 Hour":
            self.check_in_time.setVisible(True)
            self.check_out_time.setVisible(True)
            if check_in_time and check_out_time:
                self.check_in_time.setTime(QTime.fromString(check_in_time, "HH:mm"))
                self.check_out_time.setTime(QTime.fromString(check_out_time, "HH:mm"))
        else:
            self.check_in_time.setVisible(False)
            self.check_out_time.setVisible(False)

        #   Set Total Price
        self.custom_price_input.setText(f"${total_price:.2f}" if total_price else "$0.00")
        
        self.load_available_rooms(selected_room=room_id)

        #   Delay selection of room until UI update is complete
        def select_room():
            # Ensure the room dropdown is populated before selecting the room
            if self.room_dropdown.count() > 1:  # More than just "-- Select Room --"
                room_index = self.room_dropdown.findData(room_id)
                if room_index != -1:
                    self.room_dropdown.setCurrentIndex(room_index)  #   Select the correct room
                    print(f"  Room ID {room_id} found, selecting index {room_index}")
                else:
                    print(f"⚠️ Room ID {room_id} not found in dropdown!")
            else:
                print("⏳ Waiting for rooms to load... Retrying selection.")

                # 🔁 Retry selection again after another short delay (recursive call)
                QTimer.singleShot(100, select_room)

        # ⏳ Delay execution to allow UI refresh before selection (first attempt)
        QTimer.singleShot(300, select_room)

        #   Update Button Action
        
        self.add_booking_button.setText("Update Booking")
        self.add_booking_button.clicked.disconnect()
        self.add_booking_button.clicked.connect(lambda: self.update_booking(booking_id))


    
    def update_booking(self, booking_id):
        """
        Update an existing booking while ensuring proper price calculation and payment adjustments.
        """
        #   Fetch form values
        guest_id = self.guest_dropdown.currentData()
        room_id = self.room_dropdown.currentData()
        check_in_date = self.check_in_date.date().toString("yyyy-MM-dd")
        check_out_date = self.check_out_date.date().toString("yyyy-MM-dd")
        check_in_time = self.check_in_time.time().toString("HH:mm")
        check_out_time = self.check_out_time.time().toString("HH:mm")
        price_type = self.price_type_dropdown.currentText()
        custom_price_text = self.custom_price_input.text()

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        try:
            #   Prevent room double booking (except for "3 Hour")
            if price_type != "3 Hour":
                cursor.execute("""
                    SELECT id FROM Bookings 
                    WHERE room_id = ? 
                    AND check_in_date <= ? 
                    AND check_out_date >= ?
                    AND id != ?
                """, (room_id, check_out_date, check_in_date, booking_id))

                existing_booking = cursor.fetchone()
                if existing_booking:
                    QMessageBox.warning(self, "Booking Error", "This room is already booked for the selected date.")
                    return

            #   Fetch base price from Rooms table
            cursor.execute("SELECT base_price, three_hour_price FROM Rooms WHERE id = ?", (room_id,))
            room_data = cursor.fetchone()
            base_price = room_data[0] if room_data else 0.0
            three_hour_price = room_data[1] if room_data else 0.0

            #   Calculate updated price based on `price_type`
            calculated_price = base_price  # Default to base price

            if price_type == "Low Season":
                calculated_price = base_price * 0.9  # Apply 10% discount
            elif price_type == "High Season":
                calculated_price = base_price * 1.1  # Increase by 10%
            elif price_type == "3 Hour":
                # Use custom price if provided; otherwise, fallback to three_hour_price
                try:
                    custom_price = float(custom_price_text) if custom_price_text else None
                except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid custom price for '3 Hour' booking!")
                    return

                calculated_price = custom_price if custom_price else three_hour_price

            #   Update the booking details
            cursor.execute("""
                UPDATE Bookings 
                SET guest_id = ?, room_id = ?, check_in_date = ?, check_in_time = ?, 
                    check_out_date = ?, check_out_time = ?, price_type = ?, 
                    calculated_price = ?
                WHERE id = ?
            """, (guest_id, room_id, check_in_date, check_in_time, check_out_date, check_out_time, price_type, calculated_price, booking_id))

            #   Update the BookingDetails table
            cursor.execute("""
                UPDATE BookingDetails
                SET check_in_date = ?, check_in_time = ?, check_out_date = ?, check_out_time = ?, 
                    calculated_price = ?, payment_status = 'PENDING'
                WHERE booking_id = ?
            """, (check_in_date, check_in_time, check_out_date, check_out_time, calculated_price, booking_id))

            #   Check for existing payments & update payment balance
            cursor.execute("""
                SELECT SUM(amount_paid) FROM Payments WHERE booking_id = ?
            """, (booking_id,))
            total_paid = cursor.fetchone()[0] or 0.0
            remaining_balance = calculated_price - total_paid

            #   Update `payment_status` in Bookings
            new_payment_status = "PAID" if remaining_balance == 0 else "HALF PAID" if total_paid > 0 else "PENDING"
            cursor.execute("""
                UPDATE Bookings
                SET payment_status = ?
                WHERE id = ?
            """, (new_payment_status, booking_id))

            conn.commit()
            QMessageBox.information(self, "Success", "Booking updated successfully!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Error updating booking: {str(e)}")
        finally:
            conn.close()

            #   Refresh UI
            self.load_bookings()
            self.reset_form()






    def delete_booking(self, booking_id):
        """ Delete a booking and free the room """
        confirm = QMessageBox.question(self, "Delete Booking", "Are you sure you want to delete this booking?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Bookings WHERE id=?", (booking_id,))
            cursor.execute("UPDATE Rooms SET status='Available' WHERE id IN (SELECT room_id FROM Bookings WHERE id=?)", (booking_id,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Success", "Booking deleted successfully!")
            self.load_bookings()

    def load_guests(self):
        """ Load guests into the dropdown with a default empty option """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        
        # Fetch guest names
        cursor.execute("SELECT id, name FROM Guests")
        guests = cursor.fetchall()
        conn.close()

        #   Clear the dropdown first
        self.guest_dropdown.clear()

        #   Add an empty option first (Placeholder)
        self.guest_dropdown.addItem("-- Select Guest --", None)

        #   Populate the dropdown with real guests
        for guest_id, name in guests:
            self.guest_dropdown.addItem(name, guest_id)  # Store guest ID as data
        
        #   Ensure the first item (empty) is selected
        self.guest_dropdown.setCurrentIndex(0)



    def load_available_rooms(self, selected_room=None):
        """ Load rooms including booked ones for editing """

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        if selected_room:
            #   If editing a booking, ensure the selected room appears in the list
            cursor.execute("""
                SELECT id, room_number FROM Rooms 
                WHERE id=? OR id NOT IN (SELECT room_id FROM Bookings)
            """, (selected_room,))
        else:
            #   Only show available rooms for new bookings
            cursor.execute("""
                SELECT id, room_number FROM Rooms 
                WHERE id NOT IN (SELECT room_id FROM Bookings)
            """)

        rooms = cursor.fetchall()
        conn.close()

        self.room_dropdown.clear()
        self.room_dropdown.addItem("-- Select Room --", None)

        for room_id, room_number in rooms:
            self.room_dropdown.addItem(room_number, room_id)

        #   Ensure first item (empty) is selected
        self.room_dropdown.setCurrentIndex(0)

        
    def validate_booking(self, check_in_date, check_out_date, check_in_time, check_out_time, price_type):
        """ Validate booking dates and times before adding or updating """

        # Convert QDate & QTime to string formats
        today_date = QDate.currentDate().toString("yyyy-MM-dd")
        check_in_qdate = QDate.fromString(check_in_date, "yyyy-MM-dd")
        check_out_qdate = QDate.fromString(check_out_date, "yyyy-MM-dd")

        check_in_qtime = QTime.fromString(check_in_time, "HH:mm")
        check_out_qtime = QTime.fromString(check_out_time, "HH:mm")

        # 🚨 Prevent past bookings
        if check_in_qdate < QDate.fromString(today_date, "yyyy-MM-dd"):
            QMessageBox.warning(self, "Error", "Check-in date cannot be in the past!")
            return False

        # 🚨 Prevent check-out before check-in
        if check_out_qdate < check_in_qdate:
            QMessageBox.warning(self, "Error", "Check-out date must be after check-in date!")
            return False

        # 🚨 Ensure correct time relation when dates are the same
        if check_in_qdate == check_out_qdate and check_out_qtime <= check_in_qtime:
            QMessageBox.warning(self, "Error", "Check-out time must be later than check-in time when the dates are the same!")
            return False

        # 🚨 Prevent "3 Hour" bookings from spanning multiple days
        if price_type == "3 Hour" and check_in_date != check_out_date:
            QMessageBox.warning(self, "Error", "For '3 Hour' bookings, check-in and check-out must be on the same day!")
            return False

        return True

            
    def toggle_price_input(self):
        """ Show/hide price input and time fields based on the selected price type """
        selected_type = self.price_type_dropdown.currentText()

        if selected_type in ["Normal", "Low Season", "High Season"]:
            self.custom_price_input.setVisible(False)  # Hide price input
            self.custom_price_label.setVisible(False) 
            self.custom_price_input.clear()

            # Hide time fields
            self.check_in_time_label.setVisible(False)
            self.check_in_time.setVisible(False)
            self.check_out_time_label.setVisible(False)
            self.check_out_time.setVisible(False)

        elif selected_type == "3 Hour":
            #   Show custom price input and time fields for "3 Hour"
            self.custom_price_input.setVisible(True)
            self.custom_price_label.setVisible(True) 

            self.check_in_time_label.setVisible(True)
            self.check_in_time.setVisible(True)
            self.check_out_time_label.setVisible(True)
            self.check_out_time.setVisible(True)

            #   Ensure valid check-in time
            if not self.check_in_time.time().isValid():
                self.check_in_time.setTime(QTime.currentTime())

            #   Automatically set check-out time (3 hours after check-in)
            self.auto_set_checkout_time()
            self.check_in_time.timeChanged.connect(self.auto_set_checkout_time)

        else:
            self.custom_price_input.setVisible(True)
            self.custom_price_label.setVisible(True) 
            self.check_in_time_label.setVisible(False)
            self.check_in_time.setVisible(False)
            self.check_out_time_label.setVisible(False)
            self.check_out_time.setVisible(False)
            
    def filter_available_rooms(self):
        """ Fetch and display available rooms based on check-in/out date and time """

        check_in_date = self.check_in_date.date().toString("yyyy-MM-dd")
        check_out_date = self.check_out_date.date().toString("yyyy-MM-dd")
        check_in_time = self.check_in_time.time().toString("HH:mm")
        check_out_time = self.check_out_time.time().toString("HH:mm")
        price_type = self.price_type_dropdown.currentText()

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        #   For "3 Hour" bookings → Ensure no **overlapping** time slots.
        if price_type == "3 Hour":
            query = """
                SELECT r.id, r.room_number 
                FROM Rooms r
                WHERE r.id NOT IN (
                    SELECT b.room_id 
                    FROM Bookings b
                    WHERE b.check_in_date = ?
                    AND (
                        (TIME(?) >= b.check_in_time AND TIME(?) < b.check_out_time)
                        OR (TIME(?) > b.check_in_time AND TIME(?) <= b.check_out_time)
                        OR (b.check_in_time >= TIME(?) AND b.check_out_time <= TIME(?))
                        OR (b.check_in_time <= TIME(?) AND b.check_out_time >= TIME(?))
                    )
                )
            """
            cursor.execute(query, (
                check_in_date, check_in_time, check_in_time, check_out_time, check_out_time,
                check_in_time, check_out_time, check_in_time, check_out_time
            ))

        #   For "Normal" bookings → Fix: Exclude **only rooms with overlapping bookings**.
        else:
            query = """
                SELECT r.id, r.room_number 
                FROM Rooms r
                WHERE r.id NOT IN (
                    SELECT b.room_id 
                    FROM Bookings b
                    WHERE (
                        --   Exclude rooms where new check-in is inside an existing booking period
                        (b.check_in_date <= ? AND b.check_out_date >= ?) 
                        AND NOT (
                            --   Allow rooms that have already checked out **before** the new check-in time
                            b.check_out_date = ? AND TIME(b.check_out_time) <= TIME(?)
                        )
                    )
                )
            """
            cursor.execute(query, (check_in_date, check_in_date, check_in_date, check_in_time))

        rooms = cursor.fetchall()
        conn.close()

        #   Update the Dropdown with Available Rooms
        self.room_dropdown.clear()
        self.room_dropdown.addItem("-- Select Room --", None)
        for room_id, room_number in rooms:
            self.room_dropdown.addItem(room_number, room_id)

    
    def add_booking(self):
        """ Add a new booking with validation """
        guest_id = self.guest_dropdown.currentData()
        room_id = self.room_dropdown.currentData()
        check_in_date = self.check_in_date.date().toString("yyyy-MM-dd")
        check_out_date = self.check_out_date.date().toString("yyyy-MM-dd")
        price_type = self.price_type_dropdown.currentText()
        check_in_time = self.check_in_time.time().toString("HH:mm")
        check_out_time = self.check_out_time.time().toString("HH:mm")

        # 🚨 Validate input
        if guest_id is None or room_id is None:
            QMessageBox.warning(self, "Error", "Guest and Room must be selected!")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        #   Determine calculated price based on price type
        calculated_price = 0

        if price_type == "Normal":
            cursor.execute("SELECT base_price FROM Rooms WHERE id=?", (room_id,))
            result = cursor.fetchone()
            if result:
                calculated_price = result[0]

        elif price_type == "Low Season":
            cursor.execute("SELECT base_price FROM Rooms WHERE id=?", (room_id,))
            result = cursor.fetchone()
            if result:
                calculated_price = result[0] * 0.9  #   Apply 10% discount

        elif price_type == "High Season":
            cursor.execute("SELECT base_price FROM Rooms WHERE id=?", (room_id,))
            result = cursor.fetchone()
            if result:
                calculated_price = result[0] * 1.1  #   Apply 10% increase

        elif price_type == "3 Hour":
            #   Try fetching three_hour_price, otherwise use custom price
            cursor.execute("SELECT three_hour_price FROM Rooms WHERE id=?", (room_id,))
            result = cursor.fetchone()
            if result and result[0] is not None:
                calculated_price = result[0]
            else:
                try:
                    calculated_price = float(self.custom_price_input.text())  #   Use user-entered custom price
                except ValueError:
                    QMessageBox.warning(self, "Error", "Invalid custom price for '3 Hour' booking!")
                    return

        # 🔍 Print debug logs before inserting
        print("\n🔍 Attempting to add booking:")
        print(f"Guest ID: {guest_id}, Room ID: {room_id}")
        print(f"Check-in Date: {check_in_date}, Check-out Date: {check_out_date}")
        print(f"Check-in Time: {check_in_time}, Check-out Time: {check_out_time}")
        print(f"Price Type: {price_type}, Calculated Price: {calculated_price}")

        #   Insert into Bookings table
        try:
            cursor.execute("""
                INSERT INTO Bookings (guest_id, room_id, check_in_date, check_out_date, check_in_time, check_out_time, price_type, calculated_price, payment_status, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (guest_id, room_id, check_in_date, check_out_date, check_in_time, check_out_time, price_type, calculated_price, "PENDING", "BOOKING"))

            conn.commit()
            QMessageBox.information(self, "Success", "Booking added successfully!")

        except sqlite3.IntegrityError as e:
            print(f" Database Integrity Error: {e}")
            QMessageBox.warning(self, "Booking failed", f"Error: {e}")

        finally:
            conn.close()
            self.load_bookings()
            self.clear_form()



    




    def toggle_price_input(self):
        """ Show/hide price input and time fields based on the selected price type """
        selected_type = self.price_type_dropdown.currentText()
        
        if selected_type == "Normal" or selected_type == "Low Season" or selected_type == "High Season":
            self.custom_price_input.setVisible(False)  # Hide custom price input
            self.custom_price_label.setVisible(False)
            self.custom_price_input.clear()

            # Hide time fields
            self.check_in_time_label.setVisible(False)
            self.check_in_time.setVisible(False)
            self.check_out_time_label.setVisible(False)
            self.check_out_time.setVisible(False)

        elif selected_type == "3 Hour":
            #   Show custom price input for "3 Hour"
            self.custom_price_input.setVisible(True)
            self.custom_price_label.setVisible(True)

            #   Show time fields for "3 Hour"
            self.check_in_time_label.setVisible(True)
            self.check_in_time.setVisible(True)
            self.check_out_time_label.setVisible(True)
            self.check_out_time.setVisible(True)

            #   Ensure the time fields are valid
            if not self.check_in_time.time().isValid():
                self.check_in_time.setTime(QTime.currentTime())  # Set default time to now

            #   Automatically set check-out time as 3 hours after check-in
            self.auto_set_checkout_time()
            self.check_in_time.timeChanged.connect(self.auto_set_checkout_time)  # Ensure real-time updates

        else:
            self.custom_price_input.setVisible(True)
            self.custom_price_label.setVisible(True)
            
            self.check_in_time_label.setVisible(False)
            self.check_in_time.setVisible(False)
            self.check_out_time_label.setVisible(False)
            self.check_out_time.setVisible(False)

    def auto_set_checkout_time(self):
        """ Automatically set check-out time as 3 hours after check-in """
        check_in_time = self.check_in_time.time()

        if not check_in_time.isValid():
            check_in_time = QTime.currentTime()  # Use current time if invalid

        check_out_time = check_in_time.addSecs(3 * 3600)  # Add 3 hours
        self.check_out_time.setTime(check_out_time)





    def cancel_booking(self):
        """ Cancel a selected booking and free the room """
        selected_row = self.booking_table.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a booking to cancel!")
            return

        #   Fetch the booking ID from the selected row
        booking_id_item = self.booking_table.item(selected_row, 0)  
        if not booking_id_item:
            QMessageBox.warning(self, "Error", "Booking ID not found!")
            return
        
        booking_id = booking_id_item.text()

        #   Ask for confirmation before canceling
        confirm = QMessageBox.question(
            self, "Cancel Booking", f"Are you sure you want to cancel booking ID {booking_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            
            try:
                #   Update booking status to "Cancelled"
                cursor.execute("UPDATE Bookings SET status='Cancelled' WHERE id=?", (booking_id,))
                
                #   Free up the room (set status back to 'Available')
                cursor.execute("""
                    UPDATE Rooms 
                    SET status='Available' 
                    WHERE id IN (SELECT room_id FROM Bookings WHERE id=?)
                """, (booking_id,))

                conn.commit()

                #   Refresh the UI after canceling
                QMessageBox.information(self, "Success", "Booking cancelled successfully!")
                self.load_bookings()

            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"Failed to cancel booking: {e}")
            
            finally:
                conn.close()




    def reset_form(self):
        """ Reset the form fields to default state after adding or updating a booking """
        
        #   Reset dropdowns to default placeholder selection
        self.guest_dropdown.setCurrentIndex(0)  # Select "-- Select Guest --"
        self.room_dropdown.setCurrentIndex(0)   # Select "-- Select Room --"
        self.price_type_dropdown.setCurrentIndex(0)  # Select "-- Select Price Type --"

        #   Clear custom price input
        self.custom_price_input.clear()
        self.custom_price_input.setVisible(False)  # Hide it
        self.custom_price_label.setVisible(False)  

        #   Reset check-in and check-out dates to today & tomorrow
        self.check_in_date.setDate(QDate.currentDate())
        self.check_out_date.setDate(QDate.currentDate().addDays(1))

        #   Reset check-in and check-out times
        self.check_in_time.setTime(QTime(12, 0))  
        self.check_out_time.setTime(QTime(10, 0))  
        self.check_in_time_label.setVisible(False)
        self.check_in_time.setVisible(False)
        self.check_out_time_label.setVisible(False)
        self.check_out_time.setVisible(False)

        #   Reset button text & behavior
        self.add_booking_button.setText("Add Booking")
        self.add_booking_button.clicked.disconnect()
        self.add_booking_button.clicked.connect(self.add_booking)