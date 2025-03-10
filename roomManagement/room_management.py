from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSizePolicy

from PyQt6.QtWidgets import QFileDialog, QLabel
from PyQt6.QtGui import QPixmap
import os
import shutil
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QIcon
import sqlite3

from roomManagement.room_image_carousel import RoomImageCarousel
from util.custom_btn import CustomButton
from util.custom_input import CustomInput
from util.custom_label_title import CustomLabelTitle


# Define the fixed directory for room images
IMAGE_DIR = os.path.join(os.path.expanduser("~"), "documents/hotel-room-images/room_img")

# Ensure the directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

class RoomManagement(QWidget):
    def __init__(self):
        super().__init__()
        self.current_room_id = None
        self.temporary_images = []
        self.initUI()



    def initUI(self):
        """ Create the new UI layout with 70% Table and 30% Form """

        #   Main Layout (Horizontal: Table 70% & Form 30%)
        main_layout = QHBoxLayout(self)

        #   Left Section (Room Table - 70%)
        table_layout = QVBoxLayout()
        table_title = QLabel("Room List")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        table_layout.addWidget(table_title)

        self.room_table = QTableWidget()
        self.room_table.setColumnCount(6)
        self.room_table.setHorizontalHeaderLabels(["ID", "Room Number", "Type", "Capacity", "Price", "Actions"])
        table_layout.addWidget(self.room_table)

        #   Right Section (Add/Edit Room Form - 30%)
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)

        #   Title Label
        title_layout = QHBoxLayout()
        title_label = QLabel("Add / Edit Room")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        title_layout.addWidget(title_label)

        self.clear_button = QPushButton()
        self.clear_button.setIcon(QIcon("icons/ic_clear_img.png"))
        self.clear_button.setFixedSize(30, 30)
        self.clear_button.setStyleSheet("background-color: #888; color: white; border-radius: 5px;")
        self.clear_button.clicked.connect(self.clear_form) 
        title_layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignRight)
        form_layout.addLayout(title_layout)
        
        #   Room Number Input
        form_layout.addWidget(CustomLabelTitle("Room Number:"))
        self.room_number_input = CustomInput(placeholder_text="Enter Room Number", height=30)
        form_layout.addWidget(self.room_number_input)

        #   Room Type Input (With Default Hint)
        form_layout.addWidget(CustomLabelTitle("Room Type:"))
        self.room_type_input = QComboBox()
        self.room_type_input.addItem("-- Select Room Type --")  # Default placeholder
        self.room_type_input.addItems([    
            "Single (1 bed)",
            "Double (1 bed for 2 people)",
            "Twin (2 separate beds for 2 people)",
            "Suite (1 bed)",
            "Suite (2 beds)",
            "Deluxe (1 bed)",
            "Deluxe (2 beds)",
            "Deluxe (3 beds)"])  # Actual room types
        self.room_type_input.setCurrentIndex(0)  # Ensure default selection
        self.room_type_input.setStyleSheet(
            "background-color: 09122C; color: white; border-radius: 5px; padding: 4px; font-size: 14px;height : 20px;"
        )
        form_layout.addWidget(self.room_type_input)


        #   Capacity Input
        form_layout.addWidget(CustomLabelTitle("Capacity:"))
        self.capacity_input = CustomInput(placeholder_text="Enter Capacity", height=30)
        form_layout.addWidget(self.capacity_input)

        #   Price Input
        form_layout.addWidget(CustomLabelTitle("Price:"))
        self.price_input = CustomInput(placeholder_text="Enter Price", height=30)
        form_layout.addWidget(self.price_input)

        #   Upload Image Button
        form_layout.addWidget(CustomLabelTitle("Room Images:"))
        self.upload_button = CustomButton("Upload Images", "#0277bd", "icons/ic_upload.png", height=30)
        self.upload_button.clicked.connect(self.upload_images)  # Connect to function
        form_layout.addWidget(self.upload_button)

        #   Image Carousel
        self.room_image_carousel = RoomImageCarousel(self.current_room_id)
        form_layout.addWidget(self.room_image_carousel)

        self.add_button = CustomButton("Add Room", "#017f28", "icons/ic_add.png", height=30)
        self.add_button.clicked.connect(self.add_room)
        form_layout.addWidget(self.add_button)

        form_layout.addStretch() 
        form_layout.addStretch() 

        # Styling for Form Section
        form_layout.addStretch()

        # Styling for Form Section
        form_frame.setStyleSheet("background-color: #333; border-radius: 10px; padding: 5px;")

        main_layout.addLayout(table_layout, 7)
        main_layout.addWidget(form_frame, 3)

        self.setLayout(main_layout)
        self.load_rooms()

    def upload_images(self):
        """ Select multiple images but do not save them until 'Update Room' is clicked. """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return

        #   Remove previously selected temporary images before adding new ones
        self.temporary_images.clear()
        self.room_image_carousel.clear_images()

        #   Store images in temporary memory but do NOT save yet
        self.temporary_images.extend(files)

        #   Show images in the carousel immediately (but not save them)
        for file in self.temporary_images:
            self.room_image_carousel.add_image_to_carousel(file, is_temporary=True)

        QMessageBox.information(self, "Success", f"{len(files)} images added temporarily!")

    def load_rooms(self):
        """ Load and display room data in the table with Edit & Delete buttons in Actions column """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, room_number, room_type, capacity, base_price FROM Rooms")
        rooms = cursor.fetchall()
        conn.close()

        self.room_table.setRowCount(len(rooms))
        self.room_table.setColumnCount(6)
        self.room_table.setHorizontalHeaderLabels(["ID", "Room Number", "Type", "Capacity", "Price", "Actions"])

        for row, (room_id, room_no, room_type, capacity, price) in enumerate(rooms):
            self.room_table.setItem(row, 0, QTableWidgetItem(str(room_id)))
            self.room_table.setItem(row, 1, QTableWidgetItem(room_no))
            self.room_table.setItem(row, 2, QTableWidgetItem(room_type))
            self.room_table.setItem(row, 3, QTableWidgetItem(str(capacity)))
            self.room_table.setItem(row, 4, QTableWidgetItem(f"${price}"))

            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)

            # Edit Icon Button
            edit_button = QPushButton()
            edit_button.setIcon(QIcon("icons/ic_edit.png"))  # Use edit icon
            edit_button.setFixedSize(30, 30)  # Set button size
            edit_button.setStyleSheet("border: none;")  # Remove button border
            edit_button.clicked.connect(lambda _, r_id=room_id: self.edit_room(r_id))
            action_layout.addWidget(edit_button)

            # Delete Icon Button
            delete_button = QPushButton()
            delete_button.setIcon(QIcon("icons/ic_delete.png"))  # Use delete icon
            delete_button.setFixedSize(30, 30)  # Set button size
            delete_button.setStyleSheet("border: none;")  # Remove button border
            delete_button.clicked.connect(lambda _, r_id=room_id: self.delete_room(r_id))
            action_layout.addWidget(delete_button)

            action_widget.setLayout(action_layout)
            self.room_table.setCellWidget(row, 5, action_widget)

    def add_room(self):
        """ Add a new room along with images """
        room_no = self.room_number_input.text()
        room_type = self.room_type_input.currentText()
        capacity = self.capacity_input.text()
        base_price = self.price_input.text()

        if not room_no or not capacity or not base_price:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Rooms (room_number, room_type, capacity, base_price) VALUES (?, ?, ?, ?)",
                       (room_no, room_type, capacity, base_price))
        conn.commit()
        self.current_room_id = cursor.lastrowid  # Get the new room ID

        # Save room images
        for file_path in self.room_image_carousel.temporary_images:
            filename = os.path.basename(file_path)
            new_path = os.path.join(IMAGE_DIR, filename)
            shutil.copy(file_path, new_path)
            cursor.execute("INSERT INTO RoomImages (room_id, image_path) VALUES (?, ?)",
                           (self.current_room_id, filename))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Room added successfully!")
        self.load_rooms()
        self.clear_form()
        self.room_image_carousel.load_room_images()



    def edit_room(self, room_id):
        """ Edit room details including showing the stored image in the carousel """
        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT room_number, room_type, capacity, base_price FROM Rooms WHERE id=?", (room_id,))
        room = cursor.fetchone()
        conn.close()

        if not room:
            QMessageBox.warning(self, "Error", "Room not found!")
            return

        self.current_room_id = room_id  #   Ensure room ID is updated
        self.room_image_carousel.room_id = room_id  #   Assign room ID to ImageCarousel
        self.room_image_carousel.load_room_images()  #   Load images for this room

        self.room_number_input.setText(room[0])
        self.room_type_input.setCurrentText(room[1])
        self.capacity_input.setText(str(room[2]))
        self.price_input.setText(str(room[3]))

        self.add_button.setText("Update Room")
        self.add_button.clicked.disconnect()
        self.add_button.clicked.connect(lambda: self.update_room(room_id))



    def update_room(self, room_id):
        """ Update room details and save images only when 'Update Room' is clicked. """
        room_no = self.room_number_input.text().strip()
        room_type = self.room_type_input.currentText().strip()
        capacity = self.capacity_input.text().strip()
        base_price = self.price_input.text().strip()

        if not room_no or not capacity or not base_price:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()

        #   Update Room Info
        cursor.execute("""
            UPDATE Rooms 
            SET room_number=?, room_type=?, capacity=?, base_price=?
            WHERE id=?
        """, (room_no, room_type, capacity, base_price, room_id))

        #   Now save the images from temporary memory (ONLY when clicking 'Update Room')
        for file_path in self.temporary_images:
            file_name = os.path.basename(file_path)
            new_path = os.path.join(IMAGE_DIR, file_name)
            shutil.copy(file_path, new_path)  #   Copy image to permanent storage

            cursor.execute("INSERT INTO RoomImages (room_id, image_path) VALUES (?, ?)", (room_id, file_name))

        conn.commit()
        conn.close()

        #   Clear temporary images after saving
        self.temporary_images.clear()

        QMessageBox.information(self, "Success", "Room updated successfully!")
        self.load_rooms()
        self.room_image_carousel.load_room_images()

        #   Reset button to "Add Room"
        self.add_button.setText("Add Room")
        try:
            self.add_button.clicked.disconnect()
        except TypeError:
            pass
        self.add_button.clicked.connect(self.add_room)




    def delete_room(self, room_id):
        """ Deletes a room and removes its image from 'hotel-room-images/' if no other room is using it. """
        confirm = QMessageBox.question(self, "Delete Room", "Are you sure you want to delete this room?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()

            # Get the image filename before deleting the room
            cursor.execute("SELECT image_path FROM Rooms WHERE id=?", (room_id,))
            result = cursor.fetchone()
            image_filename = result[0] if result else None

            # Delete the room from the database
            cursor.execute("DELETE FROM Rooms WHERE id=?", (room_id,))
            conn.commit()

            # Check if the image is still used by any other room
            if image_filename:
                cursor.execute("SELECT COUNT(*) FROM Rooms WHERE image_path=?", (image_filename,))
                count = cursor.fetchone()[0]

                if count == 0:  # If no other rooms use the image, delete the file
                    image_path = os.path.join(os.path.expanduser("~"), "documents/hotel-room-images", image_filename)
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                            print(f"Deleted image: {image_path}")  # Log deletion
                        except Exception as e:
                            print(f" Error deleting image: {str(e)}")

            conn.close()
            QMessageBox.information(self, "Success", "Room deleted successfully!")
            self.load_rooms()

    def upload_images(self):
        """ Allow users to select multiple images and ensure they update correctly in the carousel. """
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not files:
            return

        #   Clear old images before adding new ones
        self.room_image_carousel.clear_images()
        self.temporary_images.clear()

        if self.current_room_id is None:
            #   Store new images temporarily
            self.temporary_images.extend(files)
            for file in self.temporary_images:
                self.room_image_carousel.add_image_to_carousel(file, is_temporary=True)
            
            QMessageBox.information(self, "Success", f"{len(files)} images added temporarily!")
        
        else:
            #   Save images directly to the database
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()

            for file_path in files:
                file_name = os.path.basename(file_path)
                new_path = os.path.join(IMAGE_DIR, file_name)

                try:
                    shutil.copy(file_path, new_path)  #   Copy image to the correct directory
                    cursor.execute("INSERT INTO RoomImages (room_id, image_path) VALUES (?, ?)", 
                                (self.current_room_id, file_name))
                    self.room_image_carousel.add_image_to_carousel(new_path, is_temporary=False)  #   Show in UI
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to save image: {str(e)}")

            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", f"{len(files)} images uploaded!")

        #   Update image carousel properly
        self.room_image_carousel.room_id = self.current_room_id
        self.room_image_carousel.load_room_images()

    def clear_form(self):
        """ Completely resets the form, images, and button state. """
        #   Clear all input fields
        self.room_number_input.clear()
        self.room_type_input.setCurrentIndex(0)
        self.capacity_input.clear()
        self.price_input.clear()

        #   Clear image carousel & temporary images
        self.room_image_carousel.clear_images()
        self.temporary_images.clear()  #   Also clear the temporary list

        #   Reset room ID
        self.current_room_id = None

        #   Reset button to "Add Room"
        self.add_button.setText("Add Room")
        
        #   Disconnect previous signals and reconnect "Add Room"
        try:
            self.add_button.clicked.disconnect()
        except TypeError:
            pass  # Ignore if no previous connection

        self.add_button.clicked.connect(self.add_room)

        #   Ensure UI refresh
        self.repaint()  # Force update UI if needed

    def refresh_room_list(self):
        """ Refresh the room list and update the UI """
        self.load_rooms()  
        self.clear_form()  
