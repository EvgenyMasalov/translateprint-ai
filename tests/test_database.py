import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User
import uuid

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_user_creation():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        first_name="Test",
        last_name="User",
        email="test@example.com"
    )
    db.add(new_user)
    db.commit()
    
    db_user = db.query(User).filter(User.email == "test@example.com").first()
    assert db_user is not None
    assert db_user.first_name == "Test"
    assert db_user.id == user_id
    
    db.close()
