import unittest
import os
from app.core.security import create_access_token, decode_access_token
from app.core.config import settings

class TestAuthUtils(unittest.TestCase):
    def setUp(self):
        settings.JWT_SECRET = "test-secret"

    def test_create_and_decode_token(self):
        email = "test@example.com"
        token = create_access_token(subject=email)
        decoded = decode_access_token(token)
        
        self.assertIsNotNone(token)
        self.assertEqual(decoded["sub"], email)
        self.assertIn("exp", decoded)

    def test_decode_invalid_token(self):
        invalid_token = "invalid-token-string"
        decoded = decode_access_token(invalid_token)
        self.assertIsNone(decoded)

if __name__ == '__main__':
    unittest.main()
