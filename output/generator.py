import os
import zipfile
from datetime import datetime
from typing import List
from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

from core.session import Session, SessionEndReason

# Authoritative constant from docs/04_output.md
ADMIN_PASSWORD = "adminv1"


class OutputGenerator:
    """
    Handles generation of PDF reports and packaging them into a ZIP file.
    Ref: docs/04_output.md
    """

    def generate_package(self, sessions: List[Session], output_path: str, user_name: str = "Employee", hourly_rate: float = 0.0):
        """
        Creates a ZIP file containing invoice.pdf and administrative_record.pdf.
        """
        invoice_data = self._render_invoice(sessions, user_name, hourly_rate)
        admin_record_data = self._render_administrative_record(sessions, user_name)
        
        # Encrypt the administrative record
        encrypted_admin_record = self._encrypt_pdf(admin_record_data, ADMIN_PASSWORD)

        with zipfile.ZipFile(output_path, 'w') as zf:
            zf.writestr("invoice.pdf", invoice_data)
            zf.writestr("administrative_record.pdf", encrypted_admin_record)

    def _render_invoice(self, sessions: List[Session], user_name: str, hourly_rate: float) -> bytes:
        """
        Renders the invoice PDF. Does not expose inactivity details.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"INVOICE - {user_name}")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(50, height - 100, f"Hourly Rate: Php {hourly_rate:,.2f} / hour")
        
        y = height - 140
        c.drawString(50, y, "Start Time")
        c.drawString(200, y, "End Time")
        c.drawString(350, y, "Duration (h)")
        c.drawString(450, y, "Task")
        
        y -= 20
        c.line(50, y + 15, 550, y + 15)
        
        total_seconds = 0
        for s in sessions:
            if not s.is_complete:
                continue
            
            duration = s.get_duration_seconds()
            total_seconds += duration
            duration_hours = duration / 3600.0
            
            c.drawString(50, y, s.start_time.strftime('%Y-%m-%d %H:%M:%S'))
            c.drawString(200, y, s.end_time.strftime('%Y-%m-%d %H:%M:%S'))
            c.drawString(350, y, f"{duration_hours:.4f}")
            c.drawString(450, y, s.task[:20])
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50

        y -= 10
        c.line(50, y + 5, 550, y + 5)
        c.setFont("Helvetica-Bold", 12)
        
        total_hours = total_seconds / 3600.0
        amount_to_be_paid = hourly_rate * total_hours
        
        c.drawString(50, y - 15, f"ACCUMULATED SESSION TIME (AST): {total_hours:.4f} hours")
        c.drawString(50, y - 35, f"AMOUNT TO BE PAID: Php {amount_to_be_paid:,.2f}")

        c.save()
        return buffer.getvalue()

    def _render_administrative_record(self, sessions: List[Session], user_name: str) -> bytes:
        """
        Renders the administrative record PDF. Includes inactivity details and end reasons.
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=LETTER)
        width, height = LETTER

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"ADMINISTRATIVE RECORD - {user_name}")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        y = height - 120
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Start")
        c.drawString(150, y, "End")
        c.drawString(250, y, "Dur(s)")
        c.drawString(300, y, "Inact(s)")
        c.drawString(350, y, "Reason")
        c.drawString(450, y, "Task")
        
        y -= 20
        c.line(50, y + 15, 550, y + 15)
        
        c.setFont("Helvetica", 9)
        total_seconds = 0
        for s in sessions:
            if not s.is_complete:
                continue
            
            duration = s.get_duration_seconds()
            total_seconds += duration
            
            c.drawString(50, y, s.start_time.strftime('%y-%m-%d %H:%M'))
            c.drawString(150, y, s.end_time.strftime('%y-%m-%d %H:%M'))
            c.drawString(250, y, str(duration))
            c.drawString(300, y, str(s.max_inactivity_reached_seconds))
            c.drawString(350, y, s.end_reason.name if s.end_reason else "N/A")
            c.drawString(450, y, s.task[:15])
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50

        y -= 10
        c.line(50, y + 5, 550, y + 5)
        c.setFont("Helvetica-Bold", 12)
        
        total_hours = total_seconds / 3600.0
        c.drawString(50, y - 15, f"ACCUMULATED SESSION TIME (AST): {total_hours:.4f} hours")

        c.save()
        return buffer.getvalue()

    def _encrypt_pdf(self, pdf_data: bytes, password: str) -> bytes:
        """
        Encrypts the PDF data with the given password.
        """
        reader = PdfReader(BytesIO(pdf_data))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        writer.encrypt(password)
        
        buffer = BytesIO()
        writer.write(buffer)
        return buffer.getvalue()
