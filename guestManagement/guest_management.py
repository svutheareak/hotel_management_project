import os
import shutil
import time
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QFrame, QScrollArea, QGridLayout, QFileDialog, QDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

from guestManagement.guest_preview_dialog import GuestPreviewDialog
from util.custom_btn import CustomButton
from util.custom_input import CustomInput
from util.custom_label_title import CustomLabelTitle
from util.image_carousel import ImageCarousel
from util.imgpop import ImagePopup

#   Define Guest Image Directory
GUEST_IMAGE_DIR = os.path.join(os.path.expanduser("~"), "documents/hotel-room-images/guest_img")

#   Ensure directory exists
os.makedirs(GUEST_IMAGE_DIR, exist_ok=True)


class GuestManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_guest_id = None
        self.temporary_images = []
        self.initUI()

    def initUI(self):
        """ Create the Guest Management UI layout """

        #   Main Layout (Table on Left, Form on Right)
        main_layout = QHBoxLayout(self)

        #   Left Section (Guest List Table)
        table_layout = QVBoxLayout()
        table_title = QLabel("Guest List")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.guest_table = QTableWidget()
        self.guest_table.setColumnCount(5)
        self.guest_table.setHorizontalHeaderLabels(["ID", "Name", "Contact", "Email", "Actions"])
        table_layout.addWidget(self.guest_table)

        #   Right Section (Add/Edit Guest Form)
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)

        #   Title Label
        title_layout = QHBoxLayout()
        title_label = QLabel("Add / Edit Guest")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)

        self.clear_button = QPushButton()
        self.clear_button.setIcon(QIcon("icons/ic_clear_img.png"))
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.setStyleSheet("background-color: #888; color: white; border-radius: 5px;")
        self.clear_button.clicked.connect(self.clear_form) 
        title_layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignRight)

        form_layout.addLayout(title_layout)

        #   Guest Name Input
        form_layout.addWidget(CustomLabelTitle("Name:"))
        self.name_input = CustomInput(placeholder_text="Full Name", height=30)
        form_layout.addWidget(self.name_input)

        #   Contact Input
        form_layout.addWidget(CustomLabelTitle("Contact:"))
        self.contact_input = CustomInput(placeholder_text="Phone Number", height=30)
        form_layout.addWidget(self.contact_input)

        #   Email Input
        form_layout.addWidget(CustomLabelTitle("Email:"))
        self.email_input = CustomInput(placeholder_text="Email (Optional)", height=30)
        form_layout.addWidget(self.email_input)

        #   Upload Image Section
        form_layout.addWidget(CustomLabelTitle("Guest Images:"))
        self.upload_button = CustomButton("Upload Images", "#0277bd", "icons/ic_upload.png", height=30)
        self.upload_button.clicked.connect(self.upload_images)
        form_layout.addWidget(self.upload_button)

        #   Image Carousel
        self.image_carousel = ImageCarousel(self.current_guest_id)
        form_layout.addWidget(self.image_carousel)

        #   Add Button
        self.add_guest_button = CustomButton("Add Guest", "#017f28", "icons/ic_add.png", height=30)
        self.add_guest_button.clicked.connect(self.add_guest)
        form_layout.addWidget(self.add_guest_button)

        form_layout.addStretch()

        #   Combine Layouts (70% Table, 30% Form)
        main_layout.addLayout(table_layout, 7)
        main_layout.addWidget(form_frame, 3)

        self.setLayout(main_layout)
        self.load_guests()

    def load_guests(self):
        """ Load all guests into the table """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, contact, email FROM Guests")
        guests = cursor.fetchall()
        conn.close()

        self.guest_table.setRowCount(len(guests))
        self.guest_table.setColumnCount(5)  
        self.guest_table.setHorizontalHeaderLabels(["ID", "Name", "Contact", "Email", "Actions"])

        #   Hide row numbers
        self.guest_table.verticalHeader().setVisible(True)

        #   Set fixed column widths
        self.guest_table.setColumnWidth(0, 50)   # ID Column
        self.guest_table.setColumnWidth(1, 150)  # Name Column
        self.guest_table.setColumnWidth(2, 120)  # Contact Column
        self.guest_table.setColumnWidth(3, 200)  # Email Column
        self.guest_table.setColumnWidth(4, 80)   # Actions Column

        #   Make last column non-expandable
        self.guest_table.horizontalHeader().setStretchLastSection(True)

        for row, (guest_id, name, contact, email) in enumerate(guests):
            self.guest_table.setItem(row, 0, QTableWidgetItem(str(guest_id)))
            self.guest_table.setItem(row, 1, QTableWidgetItem(name))
            self.guest_table.setItem(row, 2, QTableWidgetItem(contact))
            self.guest_table.setItem(row, 3, QTableWidgetItem(email or "N/A"))

            #   Add Edit & Delete Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)  # Reduce spacing between buttons

            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icons/ic_edit.png"))
            edit_button.setStyleSheet("border: none;")
            edit_button.setFixedSize(25, 25)  # Adjust button size
            edit_button.clicked.connect(lambda _, g_id=guest_id: self.edit_guest(g_id))
            action_layout.addWidget(edit_button)

            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icons/ic_delete.png"))
            delete_button.setFixedSize(25, 25)  
            delete_button.setStyleSheet("border: none;")
            delete_button.clicked.connect(lambda _, g_id=guest_id: self.delete_guest(g_id))
            action_layout.addWidget(delete_button)

            # 🖨 Print/Preview PDF Button
            print_button = QPushButton()
            print_button.setIcon(QIcon("icons/ic_printer.png"))  # Ensure you have an icon named "ic_print.png"
            print_button.setFixedSize(25, 25)
            print_button.setStyleSheet("border: none;")
            print_button.clicked.connect(lambda _, g_id=guest_id: self.print_guest_details(g_id))
            action_layout.addWidget(print_button)
            
             # 🔥 **History Button**
            history_button = QPushButton()
            history_button.setIcon(QIcon("icons/ic_history.png"))  # Use an appropriate icon
            history_button.setFixedSize(25, 25)
            history_button.setStyleSheet("border: none;")
            history_button.clicked.connect(lambda _, g_id=guest_id: self.show_guest_history(g_id))
            action_layout.addWidget(history_button)

            action_widget.setLayout(action_layout)
            self.guest_table.setCellWidget(row, 4, action_widget)




    def add_guest(self):
        """ Add a new guest and display images in the image carousel immediately. """
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "Name and Contact are required!")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        #   Insert guest first and get the new guest ID
        cursor.execute("INSERT INTO Guests (name, contact, email) VALUES (?, ?, ?)", (name, contact, email))
        conn.commit()
        self.current_guest_id = cursor.lastrowid  #   Assign guest ID immediately

        #   Copy all stored images for this guest
        saved_image_paths = []  #   Store image filenames for loading them later
        for file_path in self.temporary_images:
            file_extension = os.path.splitext(file_path)[1].lower()
            original_filename = os.path.basename(file_path)
            timestamp = int(time.time() * 1000000)  # Use microseconds for uniqueness
            new_filename = f"guest_{self.current_guest_id}_{timestamp}_{original_filename}"
            new_path = os.path.join(GUEST_IMAGE_DIR, new_filename)

            try:
                shutil.copy(file_path, new_path)  #   Copy image
                cursor.execute("INSERT INTO GuestImages (guest_id, image_path) VALUES (?, ?)", (self.current_guest_id, new_filename))
                saved_image_paths.append(new_filename)  #   Save filenames for later use
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

        conn.commit()
        conn.close()

        #   Clear temporary images
        self.temporary_images.clear()

        QMessageBox.information(self, "Success", "Guest added successfully with images!")

        #   Refresh UI
        self.load_guests()
        self.clear_form()

        #   Load images into carousel AFTER guest ID is assigned and images are saved
        self.image_carousel.guest_id = self.current_guest_id  
        self.image_carousel.load_guest_images()  #   Now images will appear immediately!



    def edit_guest(self, guest_id):
        """ Load guest details and images into the form """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, contact, email FROM Guests WHERE id=?", (guest_id,))
        guest = cursor.fetchone()
        conn.close()

        if not guest:
            QMessageBox.warning(self, "Error", "Guest not found!")
            return

        self.current_guest_id = guest_id  #   Ensure guest ID is updated
        self.image_carousel.guest_id = guest_id  #   Assign guest ID to ImageCarousel
        self.image_carousel.load_guest_images()  #   Load images for this guest

        self.name_input.setText(guest[0])
        self.contact_input.setText(guest[1])
        self.email_input.setText(guest[2] if guest[2] else "")

        self.add_guest_button.setText("Update Guest")
        self.add_guest_button.clicked.disconnect()
        self.add_guest_button.clicked.connect(lambda: self.update_guest(guest_id))

    def update_guest(self, guest_id):
        """ Update guest details in the database and clear data after success """
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not contact:
            QMessageBox.warning(self, "Input Error", "Name and Contact are required!")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE Guests SET name=?, contact=?, email=? WHERE id=?", (name, contact, email, guest_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Guest updated successfully!")

        #   Refresh guest list
        self.load_guests()

        #   Clear all fields and reset image carousel
        self.clear_form()



    def delete_guest(self, guest_id):
        """ Delete a guest only if they have no active bookings """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Bookings WHERE guest_id=?", (guest_id,))
        active_bookings = cursor.fetchone()[0]

        if active_bookings > 0:
            QMessageBox.warning(self, "Error", "Cannot delete guest with active bookings!")
            return

        cursor.execute("DELETE FROM Guests WHERE id=?", (guest_id,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Guest deleted successfully!")
        self.load_guests()

    def upload_images(self):
        """ Allow users to select multiple images and store them correctly based on guest status. """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return

        if self.current_guest_id is None:
            #   NEW: Clear all images when adding a new guest
            self.image_carousel.clear_images()
            self.temporary_images.clear()

            #   Store images temporarily before saving
            self.temporary_images.extend(files)
            for file in self.temporary_images:
                self.image_carousel.add_image_to_carousel(file, is_temporary=True)  #   Show immediately
            
            QMessageBox.information(self, "Success", f"{len(files)} images added temporarily!")

        else:
            #   Edit flow (DO NOT CLEAR IMAGES)
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()

            for file_path in files:
                file_extension = os.path.splitext(file_path)[1].lower()
                original_filename = os.path.basename(file_path)
                valid_extensions = {".png", ".jpg", ".jpeg", ".bmp"}

                if file_extension not in valid_extensions:
                    QMessageBox.warning(self, "Error", "Invalid file type! Please upload an image.")
                    continue

                #   Generate a unique filename using guest ID, timestamp, and original filename
                timestamp = int(time.time() * 1000000)  # Use microseconds to ensure uniqueness
                new_filename = f"guest_{self.current_guest_id}_{timestamp}_{original_filename}"
                new_path = os.path.join(GUEST_IMAGE_DIR, new_filename)

                try:
                    shutil.copy(file_path, new_path)  #   Copy image to the correct directory
                    cursor.execute("INSERT INTO GuestImages (guest_id, image_path) VALUES (?, ?)", (self.current_guest_id, new_filename))
                    self.image_carousel.add_image_to_carousel(new_path, is_temporary=False)  #   Load into UI
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"{len(files)} images uploaded!")

        #   Ensure images appear properly
        self.image_carousel.guest_id = self.current_guest_id
        self.image_carousel.load_guest_images()


    def clear_selected_image(self):
        """ Clears the selected image before it is uploaded """
        self.selected_image_path = None
        self.image_carousel.clear_images()  # Remove image from the UI
    
    def load_guest_images(self, guest_id):
        """ Load and display guest images with delete buttons properly aligned """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, image_path FROM GuestImages WHERE guest_id=?", (guest_id,))
        images = cursor.fetchall()
        conn.close()

        #   Clear existing images before adding new ones
        self.image_carousel.clear_images()

        if not images:
            print("⚠️ No images found for this guest.")
            return

        for image_id, image_filename in images:
            image_path = os.path.join(GUEST_IMAGE_DIR, image_filename)

            if os.path.exists(image_path):
                #   Create image display container
                image_container = QWidget()
                container_layout = QVBoxLayout(image_container)  
                container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                #   Create Delete Button
                delete_button = QPushButton()
                delete_button.setIcon(QIcon("icons/ic_delete.png"))
                delete_button.setFixedSize(24, 24)  
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: red; 
                        border-radius: 12px;
                        padding: 2px;
                    }
                    QPushButton:hover {
                        background-color: darkred;
                    }
                """)
                delete_button.clicked.connect(lambda _, img_id=image_id: self.delete_guest_image(img_id))

                #   Create Clickable Image Label
                image_label = QLabel()
                pixmap = QPixmap(image_path).scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(200, 150)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_label.setCursor(Qt.CursorShape.PointingHandCursor)  
                image_label.mousePressEvent = lambda event, img=image_path: self.view_image(img)  

                #   Add delete button above image
                container_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignCenter)
                container_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

                #   Add the full image container to the carousel
                self.image_carousel.image_stack.addWidget(image_container)
            else:
                print(f"⚠️ Warning: Image file not found: {image_path}")





    def delete_guest_image(self, image_id):
        """ Delete guest image from the database and refresh the gallery """
        confirm = QMessageBox.question(
            self, "Delete Image", "Are you sure you want to delete this image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            
            #   Get the image path before deleting
            cursor.execute("SELECT image_path FROM GuestImages WHERE id=?", (image_id,))
            image = cursor.fetchone()

            if not image:
                QMessageBox.warning(self, "Error", "Image not found!")
                conn.close()
                return

            image_path = image[0]

            #   Delete the image from the database
            cursor.execute("DELETE FROM GuestImages WHERE id=?", (image_id,))
            conn.commit()
            conn.close()

            #   Remove the image file (Optional: Only if you want to delete the file from disk)
            import os
            if os.path.exists(image_path):
                os.remove(image_path)

            QMessageBox.information(self, "Success", "Image deleted successfully!")
            self.load_guest_images(self.current_guest_id)  # Refresh images

    def delete_image(self, image_id):
        """ Delete an image from the database """
        confirm = QMessageBox.question(self, "Delete Image", "Are you sure you want to delete this image?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()

            #   Get Image Path Before Deleting
            cursor.execute("SELECT image_path FROM GuestImages WHERE id=?", (image_id,))
            image_path = cursor.fetchone()

            if image_path:
                try:
                    import os
                    os.remove(image_path[0])  #   Remove the physical file from storage
                except FileNotFoundError:
                    print("⚠️ Image file not found, but removing from database")

            #   Delete from Database
            cursor.execute("DELETE FROM GuestImages WHERE id=?", (image_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Image deleted successfully!")
            self.load_guest_images(self.current_guest_id)  

    #     popup.show()
    def view_image(self, image_path):
        """ Open the image in a new window """
        print(f"🔍 Opening Image: {image_path}") 
        self.image_popup = ImagePopup(image_path) 
        self.image_popup.show()

    def print_guest_details(self, guest_id):
        """ Show a pop-up with guest details including images """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name, contact, email FROM Guests WHERE id=?", (guest_id,))
        guest = cursor.fetchone()

        if not guest:
            QMessageBox.warning(self, "Error", "Guest not found!")
            return

        #   Load guest details
        guest_name, guest_contact, guest_email = guest

        #   Load guest images from database
        cursor.execute("SELECT image_path FROM GuestImages WHERE guest_id=?", (guest_id,))
        images = [row[0] for row in cursor.fetchall()]
        conn.close()

        #   Open the pop-up window
        self.guest_preview_dialog = GuestPreviewDialog(guest_name, guest_contact, guest_email, images)
        self.guest_preview_dialog.exec()
        
    ##Show gurest Hoistory
    def show_guest_history(self, guest_id):
        """ Show a popup dialog with the booking history of the selected guest, including total amount paid """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT B.id, R.room_number, B.check_in_date, B.check_out_date, 
                B.payment_status, 
                COALESCE((SELECT SUM(amount_paid) FROM Payments WHERE booking_id = B.id), 0) AS total_amount
            FROM GuestHistory B
            JOIN Rooms R ON B.room_id = R.id
            WHERE B.guest_id = ?
            ORDER BY B.check_in_date DESC
        """, (guest_id,))
        
        history_data = cursor.fetchall()
        conn.close()

        #   Create a pop-up dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Guest Booking History")
        dialog.setMinimumSize(700, 350)

        layout = QVBoxLayout(dialog)
        history_label = QLabel("Booking History")
        history_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(history_label)

        #   Create Table
        history_table = QTableWidget()
        history_table.setColumnCount(6)  #   Added "Total Amount"
        history_table.setHorizontalHeaderLabels(["Booking ID", "Room", "Check-in", "Check-out", "Status", "Total Amount ($)"])
        history_table.setRowCount(len(history_data))

        for row_idx, row_data in enumerate(history_data):
            for col_idx, item in enumerate(row_data):
                history_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

        layout.addWidget(history_table)

        #   Add Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()



    def clear_form(self):
        """ Clears the guest form and resets the selected image """
        self.name_input.clear()
        self.contact_input.clear()
        self.email_input.clear()
        self.current_guest_id = None

        #   Reset selected image path
        self.selected_image_path = None
        self.temporary_images.clear()  #   Clear temp images

        #   Clear image preview in carousel
        if self.image_carousel:
            self.image_carousel.clear_images()

        #   Reset button text to "Add Guest"
        self.add_guest_button.setText("Add Guest")
        self.add_guest_button.clicked.disconnect()
        self.add_guest_button.clicked.connect(self.add_guest)
        
    def refresh_guest_list(self):
        """ Refresh the guest list and update the UI """
        self.load_guests() 
        self.clear_form()   



