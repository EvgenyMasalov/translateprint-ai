import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_ping(self):
        response = self.client.get("/ping")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "pong")
        self.assertIn("timestamp", data)

    def test_unauthorized_me(self):
        response = self.client.get("/me")
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
