from PyQt6.QtWidgets import QWidget,QMessageBox, QLabel, QVBoxLayout, QPushButton, QStackedWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import os
import sqlite3

from util.imgpop import ImagePopup

#   Define Image Storage Directory
ROOM_IMAGE_DIR = os.path.join(os.path.expanduser("~"), "documents/hotel-room-images/room_img")

class RoomImageCarousel(QWidget):
    def __init__(self, room_id=None):
        super().__init__()
        self.room_id = room_id
        self.image_paths = []
        self.current_index = 0
        self.temporary_images = [] 

        #   Main Layout
        self.layout = QVBoxLayout(self)

        #   Image Stack for Carousel
        self.image_stack = QStackedWidget()
        self.layout.addWidget(self.image_stack)

        #   Navigation Layout with Previous Button, Counter, and Next Button
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("<")
        self.next_button = QPushButton(">")
        self.image_counter = QLabel("0/0")  #   Number in the middle (default)

        self.prev_button.clicked.connect(self.show_prev_image)
        self.next_button.clicked.connect(self.show_next_image)

        #   Add Buttons and Counter to Layout
        nav_layout.addWidget(self.prev_button, alignment=Qt.AlignmentFlag.AlignLeft)
        nav_layout.addWidget(self.image_counter, alignment=Qt.AlignmentFlag.AlignCenter)  #   Counter in the middle
        nav_layout.addWidget(self.next_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.layout.addLayout(nav_layout)  #   Add navigation to UI

        if self.room_id:
            self.load_room_images()

    def load_room_images(self):
        """ Load room images from the database and keep the delete button in the top-right corner """
        if not self.room_id:
            return

        self.current_index = 0  #   Reset image index when switching rooms

        conn = sqlite3.connect("hotel_management.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, image_path FROM RoomImages WHERE room_id=?", (self.room_id,))
        images = cursor.fetchall()
        conn.close()

        self.image_paths = [(img[0], os.path.join(ROOM_IMAGE_DIR, img[1])) for img in images]

        #   Clear previous images but keep delete functionality
        while self.image_stack.count():
            widget = self.image_stack.widget(0)
            self.image_stack.removeWidget(widget)
            widget.deleteLater()

        if not self.image_paths:
            self.image_counter.setText("0/0")  #   No images available
            return

        for image_id, image_path in self.image_paths:
            if os.path.exists(image_path):
                #   Create Image Display Container
                image_container = QWidget()
                container_layout = QVBoxLayout(image_container)
                container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                #   Create Image Holder with Overlay Layout
                image_holder = QWidget()
                image_holder_layout = QVBoxLayout(image_holder)
                image_holder_layout.setContentsMargins(0, 0, 0, 0)  #   Remove margins
                image_holder_layout.setSpacing(0)

                #   Create Clickable Image Label
                image_label = QLabel()
                pixmap = QPixmap(image_path).scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
                image_label.setPixmap(pixmap)
                image_label.setFixedSize(250, 150)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                image_label.setCursor(Qt.CursorShape.PointingHandCursor)
                image_label.mousePressEvent = lambda event, img=image_path: self.view_image(img)

                #   Delete Button (Properly Positioned in Top-Right)
                delete_button = QPushButton()
                delete_button.setFixedSize(30, 30)
                delete_button.setIcon(QIcon("icons/ic_close.png"))
                delete_button.setStyleSheet("""
                    QPushButton {
                        background-color: red; 
                        color: white;
                        border-radius: 15px;
                        font-weight: bold;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: darkred;
                    }
                """)
                delete_button.clicked.connect(lambda _, img_id=image_id: self.delete_room_image(img_id))  #   Delete on click

                #   Create a **QHBoxLayout** to Overlay the Delete Button on the Image
                button_layout = QHBoxLayout()
                button_layout.addStretch()  #   Push delete button to the right
                button_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

                #   Add Components to Image Holder
                image_holder_layout.addLayout(button_layout)  #   Delete button inside image
                image_holder_layout.addWidget(image_label)
                image_holder.setLayout(image_holder_layout)

                #   Add Image Holder to the Container
                container_layout.addWidget(image_holder, alignment=Qt.AlignmentFlag.AlignCenter)

                #   Add to the carousel
                self.image_stack.addWidget(image_container)

        self.image_stack.setCurrentIndex(0)  #   Ensure first image is displayed
        self.update_image_counter()  #   Update counter when switching room


    def show_prev_image(self):
        """ Show the previous image in the stack """
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.image_stack.setCurrentIndex(self.current_index)
            self.update_image_counter()

    def show_next_image(self):
        """ Show the next image in the stack """
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.image_stack.setCurrentIndex(self.current_index)
            self.update_image_counter()

    def delete_room_image(self, image_id):
        """ Delete room image from database and refresh the UI. """
        confirm = QMessageBox.question(
            self, "Delete Image", "Are you sure you want to delete this image?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()

            cursor.execute("SELECT image_path FROM RoomImages WHERE id=?", (image_id,))
            image = cursor.fetchone()
            conn.close()

            if image:
                image_path = os.path.join(ROOM_IMAGE_DIR, image[0])
                if os.path.exists(image_path):
                    os.remove(image_path)  #   Delete from disk
                else:
                    print(f"⚠️ Warning: Image file not found: {image_path}")

            #   Remove from database
            conn = sqlite3.connect("hotel_management.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM RoomImages WHERE id=?", (image_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Image deleted successfully!")

            #   Reload images after deleting
            self.load_room_images()  #   Corrected: Call `load_room_images()` directly




    def view_image(self, image_path):
        """ Open the image in a full-size popup window """
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "Error", "Image file not found!")
            return

        popup = ImagePopup(image_path)
        popup.exec()  #   Correct method for PyQt6 dialogs

    def remove_temporary_image(self, file_path):
        """ Remove a temporary image before adding the room. """
        if file_path in self.temporary_images:
            self.temporary_images.remove(file_path)  #   Remove from the temporary list
            self.image_paths.remove(file_path)  #   Remove from the displayed list

        #   Remove the specific widget from QStackedWidget
        for i in range(self.image_stack.count()):
            widget = self.image_stack.widget(i)
            if isinstance(widget, QWidget):  
                image_label = widget.findChild(QLabel)  #   Get the QLabel with the image
                if image_label and image_label.pixmap():
                    if hasattr(image_label, "image_path") and image_label.image_path == file_path:
                        self.image_stack.removeWidget(widget)
                        widget.deleteLater()
                        break  #   Stop after deleting the correct image

        #   Ensure that the image counter updates
        self.update_image_counter()




    def update_image_counter(self):
        """ Update the image counter to reflect the current image index and total images """
        total_images = len(self.image_paths)
        if total_images == 0:
            self.image_counter.setText("0/0")
        else:
            self.image_counter.setText(f"{self.current_index + 1}/{total_images}")  #   Format: Current/Total
            
    def add_image_to_carousel(self, file_path, is_temporary=False):
        """ Add an image to the carousel (used when adding a new room before saving). """
        if is_temporary:
            self.temporary_images.append(file_path)  #   Store temporarily before saving

        self.image_paths.append(file_path)

        #   Create Image Display Container
        image_container = QWidget()
        container_layout = QVBoxLayout(image_container)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #   Create Delete Button (ONLY for temporary images)
        delete_button = QPushButton()
        delete_button.setFixedSize(24, 24)
        delete_button.setIcon(QIcon("icons/ic_close.png"))
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
        if is_temporary:
            delete_button.clicked.connect(lambda _, img=file_path: self.remove_temporary_image(img))  #   Delete only temporary images

        #   Create Clickable Image Label
        image_label = QLabel()
        image_label.image_path = file_path  #   Store file path in QLabel object
        pixmap = QPixmap(file_path).scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setFixedSize(250, 150)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setCursor(Qt.CursorShape.PointingHandCursor)
        image_label.mousePressEvent = lambda event, img=file_path: self.view_image(img)

        #   Add delete button ABOVE image (ONLY for new images)
        if is_temporary:
            container_layout.addWidget(delete_button, alignment=Qt.AlignmentFlag.AlignRight)
        container_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        image_container.setLayout(container_layout)

        #   Add the new image container to the carousel stack
        self.image_stack.addWidget(image_container)

        #   Update image counter
        self.update_image_counter()



    
    def clear_images(self):
        """ Clear all images from the carousel """
        while self.image_stack.count():
            widget = self.image_stack.widget(0)
            self.image_stack.removeWidget(widget)
            widget.deleteLater()

        self.image_paths = []  #   Reset image list
        self.current_index = 0  #   Reset index
        self.image_counter.setText("0/0")  #   Update counter
