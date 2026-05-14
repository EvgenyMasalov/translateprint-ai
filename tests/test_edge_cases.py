import unittest
import os
import uuid
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import httpx

# Import app components
from app.main import app
from app.core.db_session import get_db, Base
from app.models.database_models import User, Song
from app.core.config import settings

SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.ALGORITHM

# Test Database setup (File-based for reliability across connections)
TEST_DB_FILE = "./test_edge_cases_v5.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestEdgeCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        # Manually initialize app state for tests
        app.state.client = httpx.AsyncClient()

    @classmethod
    def tearDownClass(cls):
        # We try to close it, but in sync tests it might be tricky.
        # Just dispose the engine.
        engine.dispose()
        if os.path.exists(TEST_DB_FILE):
            try:
                os.remove(TEST_DB_FILE)
            except:
                pass

    def setUp(self):
        self.client = TestClient(app)
        # Clear DB before each test
        db = TestingSessionLocal()
        db.query(Song).delete()
        db.query(User).delete()
        db.commit()
        db.close()

    # --- Authentication Edge Cases ---

    def test_expired_token(self):
        payload = {"sub": "expired@test.com", "exp": datetime.now(timezone.utc) - timedelta(hours=1)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        response = self.client.get("/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid token")

    def test_malformed_token(self):
        token = "invalid.token.here"
        response = self.client.get("/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)

    def test_token_missing_sub(self):
        payload = {"name": "No Sub", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        response = self.client.get("/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid token")

    # --- Song Management Edge Cases ---

    def test_access_another_users_song(self):
        # Register user 1
        user1 = {"first_name": "U1", "last_name": "T", "email": "u1@t.com", "password": "password123"}
        self.client.post("/register", json=user1)
        token1 = self.client.post("/login", json={"email": "u1@t.com", "password": "password123"}).json()["access_token"]
        
        # Register user 2
        user2 = {"first_name": "U2", "last_name": "T", "email": "u2@t.com", "password": "password123"}
        self.client.post("/register", json=user2)
        token2 = self.client.post("/login", json={"email": "u2@t.com", "password": "password123"}).json()["access_token"]
        
        # User 1 creates song
        res_song = self.client.post("/songs", json={"title": "Private", "lyrics": "secret"}, headers={"Authorization": f"Bearer {token1}"})
        song_id = res_song.json()["id"]
        
        # User 2 tries to get it
        response = self.client.get(f"/songs/{song_id}", headers={"Authorization": f"Bearer {token2}"})
        self.assertEqual(response.status_code, 404)

    def test_create_song_with_extremely_large_lyrics(self):
        email = "large@test.com"
        password = "password123"
        self.client.post("/register", json={"first_name": "L", "last_name": "T", "email": email, "password": password})
        token = self.client.post("/login", json={"email": email, "password": password}).json()["access_token"]
        
        large_lyrics = "A" * (100 * 1024)
        song_data = {"title": "Large Song", "lyrics": large_lyrics}
        
        response = self.client.post("/songs", json=song_data, headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["lyrics"]), 100 * 1024)

    # --- Webhook Edge Cases (Mocks) ---

    @patch("httpx.AsyncClient.post")
    def test_webhook_network_error(self, mock_post):
        # Setup mock for httpx.AsyncClient.post (which call_llm uses)
        mock_post.side_effect = httpx.ConnectError("Connection refused")
        
        # Override setting to ensure call_llm is triggered (avoiding the "mock-webhook" shortcut)
        with patch.object(settings, 'N8N_ANALYZE_HARMONY_URL', "http://real-call.com"):
            payload = {"lyrics": "fail me"}
            response = self.client.post("/webhook/analyze-harmony", json=payload)
            
            # Should return 502 or 500 based on call_llm logic
            self.assertIn(response.status_code, [502, 500])
            if response.status_code == 502:
                self.assertIn("Gateway error", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
