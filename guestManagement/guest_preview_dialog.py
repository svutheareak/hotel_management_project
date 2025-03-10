
import os
from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QFont, QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import Qt, QMarginsF


#   Define Guest Image Directory
GUEST_IMAGE_DIR = os.path.join(os.path.expanduser("~"), "Documents/hotel-room-images/guest_img")

#   Ensure directory exists
os.makedirs(GUEST_IMAGE_DIR, exist_ok=True)


class GuestPreviewDialog(QDialog):
    def __init__(self, guest_name, contact, email, images):
        super().__init__()
        self.setWindowTitle("Guest Details Preview")
        self.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")

        #   Set size to 50% of A4 (scaled-down)
        self.setFixedSize(397, 562)  # Half of A4 size in pixels

        self.guest_name = guest_name
        self.contact = contact
        self.email = email
        self.images = images

        #   Main Layout
        main_layout = QVBoxLayout(self)

        #   Header Label
        title_label = QLabel("Hotel Management")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; text-align: center; color: black;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        #   Guest Details
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(20, 5, 20, 5)  # Adjusted for smaller size

        details_layout.addWidget(self.create_detail_label("Name:", guest_name))
        details_layout.addWidget(self.create_detail_label("Contact:", contact))
        details_layout.addWidget(self.create_detail_label("Email:", email or "N/A"))

        main_layout.addLayout(details_layout)

        #   Photo Label
        photo_label = QLabel("Guest Photos:")
        photo_label.setStyleSheet("font-size: 10px; font-weight: bold; color: black;")
        main_layout.addWidget(photo_label)

        #   Image Layout
        image_layout = QHBoxLayout()
        for image_filename in images:
            image_path = self.get_image_path(image_filename)

            if os.path.exists(image_path):
                image_label = QLabel()
                pixmap = QPixmap(image_path).scaled(100, 80, Qt.AspectRatioMode.KeepAspectRatio)  # Slightly larger
                image_label.setPixmap(pixmap)
                image_label.setStyleSheet("border: 1px solid gray; background-color: lightgray; padding: 2px;")
                image_layout.addWidget(image_label)
            # else:
                # print(f"Image not found: {image_path}")

        main_layout.addLayout(image_layout)

        #   Button Layout
        button_layout = QHBoxLayout()

        #   Save as PDF Button
        self.pdf_button = QPushButton("Save as PDF")
        self.pdf_button.setStyleSheet("background-color: #017f28; color: white; padding: 4px; border-radius: 3px;")
        self.pdf_button.clicked.connect(self.export_to_pdf)
        button_layout.addWidget(self.pdf_button)

        #   Close Button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("background-color: gray; color: white; padding: 4px; border-radius: 3px;")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def create_detail_label(self, title, value):
        """ Helper method to create formatted labels for details """
        label = QLabel(f"<b>{title}</b> {value}")
        label.setStyleSheet("font-size: 10px; padding: 2px; color: black;")  # Fixed font size
        return label

    def get_image_path(self, image_filename):
        """ Returns the absolute path for a guest image """
        return os.path.join(GUEST_IMAGE_DIR, image_filename)

    def export_to_pdf(self):
        """ Export guest details as a PDF file """

        default_dir = os.path.join(os.path.expanduser("~"), "Documents/hotel-room-images/pdf")

        #   Ensure directory exists
        os.makedirs(default_dir, exist_ok=True)

        #   Set default file name
        default_file_path = os.path.join(default_dir, "guest_details.pdf")

        #   Open save dialog with default path
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save as PDF", default_file_path, "PDF Files (*.pdf)"
        )

        if not file_name:
            return

        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_name)

        #   Set full A4 page size for PDF
        page_layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(20, 20, 20, 20)
        )
        printer.setPageLayout(page_layout)

        painter = QPainter()
        painter.begin(printer)

        margin_x, margin_y = 50, 1000  # Page margins
        line_spacing = 500  # More spacing between lines

        #   Title
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Reduced font size
        painter.drawText(margin_x, margin_y, "Hotel Management")

        y_offset =  margin_y + 1000 

        #   Guest Details
        painter.setFont(QFont("Arial", 10))
        painter.drawText(margin_x, y_offset, f"Name:\t\t{self.guest_name}")
        y_offset += line_spacing
        painter.drawText(margin_x, y_offset, f"Contact:\t\t{self.contact}")
        y_offset += line_spacing
        painter.drawText(margin_x, y_offset, f"Email:\t\t{self.email or 'N/A'}")
        y_offset += 2 * line_spacing

        #   Image Header
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(margin_x, y_offset, "Image:")
        y_offset += line_spacing
        printer.setResolution(72) 

        #   Ensure image scaling fits the PDF layout
        page_rect = printer.pageRect(QPrinter.Unit.Point)
        max_width = (page_rect.width() - margin_x) * 4

        #   Dynamically determine image size based on available space
        images_per_row = 2  # Adjust to allow 2 images per row
        image_width = max_width * 2 # Ensure space between images
        image_height = image_width * 0.75  # Maintain aspect ratio

        #   Draw images
        x_start = margin_x
        x, y = x_start, y_offset  # Start position for images

        for index, image_filename in enumerate(self.images):
            image_path = self.get_image_path(image_filename)

            if os.path.exists(image_path):
                pixmap = QPixmap(image_path)

                # Ensure image is valid before scaling
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(image_width, image_height, Qt.AspectRatioMode.KeepAspectRatio)

                    # painter.setBrush(Qt.GlobalColor.red)  # Red background for visibility
                    painter.setPen(Qt.GlobalColor.black)  # Black border
                    painter.drawRect(x - 5, y - 5, image_width + 10, image_height + 10)  

                    #   Draw the actual image
                    painter.drawPixmap(x, y, pixmap)
                    x += image_width + 100  # Move right for next image

                    # Move to the next row if max images per row reached
                    if (index + 1) % images_per_row == 0:
                        x = x_start
                        y += image_height + 100  # Increase row spacing for better layout
                else:
                    print(f" Skipping empty or invalid image: {image_path}")
            else:
                print(f" Skipping missing image: {image_path}")


        painter.end()
        QMessageBox.information(self, "Success", "PDF Exported Successfully!")
