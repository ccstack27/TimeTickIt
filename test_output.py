import unittest
import os
import zipfile
from datetime import datetime, timedelta
from io import BytesIO
from pypdf import PdfReader
from output.generator import OutputGenerator, ADMIN_PASSWORD
from core.session import Session, SessionEndReason

class TestOutputGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = OutputGenerator()
        self.test_zip = "test_output.zip"
        
        # Create some test sessions
        self.sessions = []
        s1 = Session(start_time=datetime(2026, 1, 1, 10, 0, 0), task="Task 1")
        s1.end(datetime(2026, 1, 1, 10, 30, 0), SessionEndReason.USER_STOPPED)
        self.sessions.append(s1)
        
        s2 = Session(start_time=datetime(2026, 1, 1, 11, 0, 0), task="Task 2")
        s2.end(datetime(2026, 1, 1, 11, 5, 0), SessionEndReason.INACTIVITY_LIMIT, inactivity_seconds=300)
        self.sessions.append(s2)

    def tearDown(self):
        if os.path.exists(self.test_zip):
            os.remove(self.test_zip)

    def test_generate_package_creates_zip_with_two_pdfs(self):
        self.generator.generate_package(self.sessions, self.test_zip)
        self.assertTrue(os.path.exists(self.test_zip))
        
        with zipfile.ZipFile(self.test_zip, 'r') as zf:
            file_list = zf.namelist()
            self.assertIn("invoice.pdf", file_list)
            self.assertIn("administrative_record.pdf", file_list)
            self.assertEqual(len(file_list), 2)

    def test_administrative_record_is_encrypted(self):
        self.generator.generate_package(self.sessions, self.test_zip)
        
        with zipfile.ZipFile(self.test_zip, 'r') as zf:
            admin_pdf_data = zf.read("administrative_record.pdf")
            
        reader = PdfReader(BytesIO(admin_pdf_data))
        self.assertTrue(reader.is_encrypted)
        
        # Verify it can be decrypted with the authoritative password
        success = reader.decrypt(ADMIN_PASSWORD)
        self.assertTrue(success)

    def test_invoice_is_not_encrypted(self):
        self.generator.generate_package(self.sessions, self.test_zip)
        
        with zipfile.ZipFile(self.test_zip, 'r') as zf:
            invoice_pdf_data = zf.read("invoice.pdf")
            
        reader = PdfReader(BytesIO(invoice_pdf_data))
        self.assertFalse(reader.is_encrypted)

if __name__ == "__main__":
    unittest.main()
