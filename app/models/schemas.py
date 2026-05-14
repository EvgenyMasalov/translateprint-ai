from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserRegister(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(UserBase):
    id: str
    avatar_url: Optional[str] = None
    contribution_level: str
    stats: dict

    class Config:
        from_attributes = True

# Song Schemas
class SongBase(BaseModel):
    title: str
    lyrics: str

class SongCreate(SongBase):
    id: Optional[str] = None
    structure: Optional[str] = None
    metaphors: Optional[str] = None
    mood: Optional[str] = None
    translation: Optional[str] = None
    refined_lyrics: Optional[str] = None
    target_language: Optional[str] = None
    musical_key: Optional[str] = None
    bpm: Optional[str] = None
    chords_verse: Optional[str] = None
    chords_chorus: Optional[str] = None

class SongResponse(SongCreate):
    id: str
    user_id: str
    updated_at: datetime

    class Config:
        from_attributes = True

# Other Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class WebhookLyricsRequest(BaseModel):
    chatInput: str
    targetLanguage: str

class WebhookHarmonyRequest(BaseModel):
    lyrics: str

class WebhookPoetRequest(BaseModel):
    analysis: str
    bridge: str
    targetLanguage: str
    literalTranslation: str
    originalLyrics: str
    metaphors: str

class WebhookEditorRequest(BaseModel):
    poetDraft: str
    structure: str
    mood: str
    targetLanguage: str

class DonationRequest(BaseModel):
    level: str
