from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QFrame, QSizePolicy, QHeaderView
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class TableWidget(QFrame):
    def __init__(self, title, max_width=550, parent=None):
        super().__init__(parent)
        self.setMaximumWidth(max_width)
        self.setStyleSheet("background-color: #6A5ACD; border-radius: 10px; ")

        layout = QVBoxLayout(self)

        #   Title Label
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 5px;")
        layout.addWidget(title_label)

        #   Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["B.ID", "Room", "Check-in", "In Time", "Check-out", "Out Time"])
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setMinimumHeight(200)
        
        self.table.setShowGrid(False)

        #   Customize Header Appearance
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) 
        self.table.horizontalHeader().setStyleSheet("background-color: #503bcd; color: white; font-weight: bold;")

        #   Enable Alternating Row Colors
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #6A5ACD;
                alternate-background-color: #6A5ACD;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #2E1A89;  /* Highlight selected row */
                color: white;
            }
        """)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self, records):
        """ Load data into the table safely """
        self.table.setRowCount(len(records))
        
        #Prevent data empty
        if not records:  
            return
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(4, 130)

        for row_idx, (booking_id, room, check_in, in_time, check_out, out_time) in enumerate(records):
            #   Prevent `None` values & empty fields
            booking_id = str(booking_id) if booking_id else "--"
            room = str(room) if room else "--"
            check_in = check_in if check_in else "--"
            in_time = in_time if in_time else "--"
            check_out = check_out if check_out else "--"
            out_time = out_time if out_time else "---"

            #   Add Data to Table
            self.table.setItem(row_idx, 0, QTableWidgetItem(booking_id))
            self.table.setItem(row_idx, 1, QTableWidgetItem(room))
            self.table.setItem(row_idx, 2, QTableWidgetItem(check_in))
            self.table.setItem(row_idx, 3, QTableWidgetItem(in_time))
            self.table.setItem(row_idx, 4, QTableWidgetItem(check_out))
            self.table.setItem(row_idx, 5, QTableWidgetItem(out_time))
            self.table.setWordWrap(True)

            #   Center Align Text
            for col in range(6):
                item = self.table.item(row_idx, col)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            #   Apply Background Colors to Rows (Alternating Effect)
            color = QColor("#6A5ACD") if row_idx % 2 == 0 else QColor("#503bcd") 
            for col in range(6):
                self.table.item(row_idx, col).setBackground(color)

        #   Auto Resize Columns to Fit Content
        self.table.resizeColumnsToContents()

