
import requests
from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QPixmap,QPainter
from PyQt6.QtCore import QTimer, Qt
from cryptography.fernet import Fernet


class QRCodeDialog(QDialog):
    """ Custom Dialog to Display QR Code with Background & API """

    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    def __init__(self, qr_image_data, order_id, update_ui_callback):
        super().__init__()

        self.setFixedSize(400, 550)
        self.setWindowTitle("QR Code Payment")

        self.order_id = order_id
        self.update_ui_callback = update_ui_callback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_payment_status)

        layout = QVBoxLayout()
        self.label = QLabel(self)

        #   Load and scale the background image
        background_pixmap = QPixmap("icons/ic_khqr_bg.png")  # Background image
        if background_pixmap.isNull():
            print("Error: Background image not loaded!")
            return

        background_pixmap = background_pixmap.scaled(360, 510, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation) 
        #   Load and scale QR Code
        qr_pixmap = QPixmap()
        qr_pixmap.loadFromData(qr_image_data)  # Load QR image data
        qr_pixmap = qr_pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        #   Merge QR Code onto Background
        final_pixmap = self.overlay_qr_on_background(background_pixmap, qr_pixmap)

        self.label.setPixmap(final_pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

        #   Start checking payment status every 15 seconds
        self.timer.start(15000)  # 15000 ms = 15 sec
        self.check_payment_status()  # Initial check

    def overlay_qr_on_background(self, background, qr):
        """ Overlay QR code on the background image at the center """
        combined = QPixmap(400, 550)  
        combined.fill(Qt.GlobalColor.transparent)

        painter = QPainter(combined)
        painter.drawPixmap((400 - background.width()) // 2, (550 - background.height()) // 2, background)  
        #   Calculate QR Code Position (Centered within background)
        qr_x = (400 - qr.width()) // 2
        qr_y = (550 - qr.height()) // 2 + 30  
        painter.drawPixmap(qr_x, qr_y, qr) 
        painter.end()

        return combined

    def check_payment_status(self):
        """ Check the payment status of the QR code """
        url = f"https://URL_FOR_RETURN_CHECK_IT_SUCCESS_OR_FAIL/{self.order_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "TOKEN_FOR_AUTH"
        }

        try:
            response = requests.get(url, headers=headers, timeout=0.3)
            response.raise_for_status()  # Raise an error for 4xx or 5xx responses

            data = response.json()  # Convert response to JSON

            if not data or "data" not in data:
                print("⚠️ Error: Empty or invalid response received!")
                return  # Exit without crashing

            status = data["data"].get("status", "")

            if status == "success":
                self.timer.stop()  
                self.accept()  #   Close the QR dialog
                QMessageBox.information(self, "Payment Success", "Payment was successful!")
                self.update_ui_callback()  #   Update the payment UI

            elif status == "closed":
                self.timer.stop()  #   Stop checking
                self.reject()  #   Close the QR dialog
                QMessageBox.warning(self, "QR Expired", "QR code expired. Please try again.")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error checking payment status: {e}")

    def closeEvent(self, event):
        """ Stop checking when the dialog is manually closed """
        self.timer.stop()
        event.accept()
