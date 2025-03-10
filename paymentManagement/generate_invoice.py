
from PyQt6.QtWidgets import QMessageBox
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import sqlite3


def generate_invoice(selected_rooms):
    """ Generate a properly formatted PDF invoice with Room Type and Correct Room Price """

    if not selected_rooms:
        QMessageBox.warning(None, "Error", "No bookings selected for invoice!")
        return

    pdf_filename = "invoice.pdf"
    pdf_path = os.path.join(os.getcwd(), pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=50, rightMargin=50)
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(name="Title", fontSize=18, alignment=1)
    title = Paragraph("Invoice", title_style)
    elements.append(title)
    elements.append(Spacer(1, 13))  

    #   Add Correct Column Headers
    data = [["B.ID", "Guest", "Room", "Room Type", "Check-in", "In Time", "Check-out", "Out Time", "Room Price", "Remain"]]

    total_price = 0  #   Track total room price

    conn = sqlite3.connect("hotel_management.db")
    cursor = conn.cursor()

    for booking_id, details in selected_rooms.items():
        room_number = details["room"]
        room_type = details.get("room_type", "Unknown")
        room_p  = details.get("room_price", "--")
        remaining_balance = details["price"]

        #   Fetch Room Type if not found
        if room_type == "Unknown":
            cursor.execute("SELECT room_type FROM Rooms WHERE TRIM(room_number) = ?", (room_number,))
            room_type_result = cursor.fetchone()
            room_type = room_type_result[0].strip() if room_type_result and room_type_result[0] else "Unknown"

        #   Fetch Room Price if not found
        if room_p == "--":
            cursor.execute("SELECT base_price FROM Rooms WHERE TRIM(room_number) = ?", (room_number,))
            room_p_result = cursor.fetchone()
            room_p = float(room_p_result[0]) if room_p_result and room_p_result[0] else 0.0  #   Convert to float

        remaining_display = "PAID" if remaining_balance == 0 else f"${remaining_balance:.2f}"

        row = [
            booking_id,
            details["guest"],
            details["room"],
            room_type,
            details["check_in"],
            details["check_in_time"],
            details["check_out"],
            details["check_out_time"],
            f"${room_p:.2f}",  
            remaining_display 
        ]
        total_price += details["price"]
        data.append(row)

    conn.close()

    #   Correctly Align "Total" Row (Matches Table Columns)
    data.append(["", "", "", "", "", "", "", "", "Total:", f"${total_price:.2f}"])

    table = Table(data, colWidths=[50, 100, 40, 70, 55, 45, 55, 45, 60, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.grey),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("FONTNAME", (-2, -1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (-2, -1), (-1, -1), 9),
        ("BACKGROUND", (-2, -1), (-1, -1), colors.lightgrey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))  

    doc.build(elements)

    QMessageBox.information(None, "Success", f"Invoice generated successfully: {pdf_path}")

    os.system(f'open "{pdf_path}"' if os.name == "posix" else f'start "" "{pdf_path}"')


