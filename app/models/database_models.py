from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.core.db_session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Null for OAuth-only users
    google_id = Column(String, unique=True, index=True, nullable=True)
    avatar_url = Column(String, nullable=True)
    contribution_level = Column(String, default="Free") # Supporter, Artist, Label
    is_premium = Column(DateTime, nullable=True) # Expiry date if applicable
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    songs = relationship("Song", back_populates="owner", cascade="all, delete-orphan")

class Song(Base):
    __tablename__ = "songs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    lyrics = Column(Text, nullable=False)
    structure = Column(Text, nullable=True)
    metaphors = Column(Text, nullable=True)
    mood = Column(Text, nullable=True)
    translation = Column(Text, nullable=True)
    refined_lyrics = Column(Text, nullable=True)
    target_language = Column(String, nullable=True)
    
    # Musical Harmony Fields
    musical_key = Column(String, nullable=True)
    bpm = Column(String, nullable=True)
    chords_verse = Column(Text, nullable=True)
    chords_chorus = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), index=True)

    # Relationship
    owner = relationship("User", back_populates="songs")
