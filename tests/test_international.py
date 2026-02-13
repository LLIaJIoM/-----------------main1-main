import unittest
from server import normalize_phone

class TestInternationalPhones(unittest.TestCase):
    def test_germany(self):
        # Germany (DE) +49
        # Mobile often 10-11 digits, Landline variable
        # Valid: +49 151 12345678 (13 digits total)
        self.assertEqual(normalize_phone("+4915112345678"), "+4915112345678")
        # Without plus
        self.assertEqual(normalize_phone("4915112345678"), "+4915112345678")
    
    def test_usa(self):
        # USA (US) +1
        # Fixed length 10 digits (excluding +1) => 11 total
        self.assertEqual(normalize_phone("+1 555 123 4567"), "+15551234567")
        self.assertEqual(normalize_phone("15551234567"), "+15551234567")

    def test_variable_length(self):
        # Some countries have shorter numbers.
        # Estonia (+372) can be 7 or 8 digits. Total 10-11.
        self.assertEqual(normalize_phone("+372 5123456"), "+3725123456")
        
        # China (+86) mobile is 11 digits => total 13.
        self.assertEqual(normalize_phone("+86 138 0013 8000"), "+8613800138000")

    def test_too_short(self):
        # < 7 digits
        self.assertIsNone(normalize_phone("123456"))
        self.assertIsNone(normalize_phone("+12345"))

    def test_too_long(self):
        # > 15 digits
        self.assertIsNone(normalize_phone("1234567890123456")) # 16 digits
        
    def test_russia_auto_correction(self):
        # Ensure the 8 -> +7 logic still works
        self.assertEqual(normalize_phone("89991234567"), "+79991234567")
        self.assertEqual(normalize_phone("+79991234567"), "+79991234567")

