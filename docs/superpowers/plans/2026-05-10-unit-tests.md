# Unit Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a comprehensive unit test suite for the translateprint-ai project covering authentication utilities, database models, and API endpoints.

**Architecture:** We use `pytest` as the testing framework. For database tests, we use an in-memory SQLite database to ensure isolation and speed. For API tests, we use FastAPI's `TestClient`.

**Tech Stack:** Python, pytest, FastAPI, SQLAlchemy, PyJWT.

---

### Task 1: Authentication Utilities Tests

**Files:**
- Create: `tests/test_auth_utils.py`
- Test: `tests/test_auth_utils.py`

- [ ] **Step 1: Write tests for token creation and decoding**

```python
import pytest
from auth_utils import create_access_token, decode_access_token
import os

def test_create_and_decode_token():
    # Setup
    os.environ["JWT_SECRET"] = "test-secret"
    data = {"sub": "test@example.com", "name": "Test User"}
    
    # Act
    token = create_access_token(data)
    decoded = decode_access_token(token)
    
    # Assert
    assert token is not None
    assert decoded["sub"] == data["sub"]
    assert decoded["name"] == data["name"]
    assert "exp" in decoded

def test_decode_invalid_token():
    # Setup
    os.environ["JWT_SECRET"] = "test-secret"
    invalid_token = "invalid-token-string"
    
    # Act
    decoded = decode_access_token(invalid_token)
    
    # Assert
    assert decoded is None
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_auth_utils.py -v`

---

### Task 2: Database Model Tests (Songs and Relationships)

**Files:**
- Modify: `tests/test_database.py`

- [ ] **Step 1: Add tests for Song creation and User-Song relationship**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Song
import uuid

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_user_song_relationship(db):
    user_id = str(uuid.uuid4())
    new_user = User(id=user_id, first_name="Test", last_name="User", email="test@example.com")
    db.add(new_user)
    db.commit()
    
    song_id = str(uuid.uuid4())
    new_song = Song(
        id=song_id,
        user_id=user_id,
        title="Test Song",
        lyrics="Test lyrics"
    )
    db.add(new_song)
    db.commit()
    
    # Assert
    db_user = db.query(User).filter(User.id == user_id).first()
    assert len(db_user.songs) == 1
    assert db_user.songs[0].title == "Test Song"
    
    db_song = db.query(Song).filter(Song.id == song_id).first()
    assert db_song.owner.email == "test@example.com"
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_database.py -v`

---

### Task 3: API Endpoint Tests (Ping and Auth)

**Files:**
- Create: `tests/test_backend.py`

- [ ] **Step 1: Write tests for basic API endpoints**

```python
import pytest
from fastapi.testclient import TestClient
from backend import app

client = TestClient(app)

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_unauthorized_me():
    response = client.get("/me")
    assert response.status_code == 401
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `pytest tests/test_backend.py -v`
