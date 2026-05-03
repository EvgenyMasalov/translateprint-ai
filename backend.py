import asyncio
import httpx
import os
import re
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
import uvicorn
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from database import init_db, get_db, User, Song
from auth_utils import create_access_token, decode_access_token

# Load environment variables
load_dotenv()

API_KEY = os.getenv("POLZA_API_KEY", "your_api_key_here")
BASE_URL = "https://polza.ai/api/v1/chat/completions"

# OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

oauth = OAuth()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Configure proxy from environment
    proxy_url = os.getenv("PROXY_URL")
    mounts = None
    if proxy_url:
        mounts = {
            "http://": httpx.AsyncHTTPTransport(proxy=proxy_url),
            "https://": httpx.AsyncHTTPTransport(proxy=proxy_url),
        }
    
    # Client for LLM and manual API calls
    app.state.client = httpx.AsyncClient(timeout=120.0, mounts=mounts, trust_env=False)
    
    # Register Google OAuth with proxy-enabled client
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
        client=app.state.client # Force Authlib to use our proxy client
    )
    
    yield
    await app.state.client.aclose()

app = FastAPI(title="LyricAI Studio Backend", lifespan=lifespan)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("Origin")
    host = request.headers.get("Host")
    print(f"Incoming Request: {request.method} {request.url.path} | Host: {host} | Origin: {origin}")
    response = await call_next(request)
    print(f"Response Status: {response.status_code}")
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5678",
        "http://127.0.0.1:5678",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("JWT_SECRET", "sessionsecret"),
    session_cookie="lyricai_session",
    same_site="lax"
)

@app.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.utcnow()}

# --- Models ---
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class SongBase(BaseModel):
    title: str
    lyrics: str
    structure: Optional[str] = None
    metaphors: Optional[str] = None
    mood: Optional[str] = None
    translation: Optional[str] = None
    refined_lyrics: Optional[str] = None
    target_language: Optional[str] = None
    # Musical fields
    musical_key: Optional[str] = None
    bpm: Optional[str] = None
    chords_verse: Optional[str] = None
    chords_chorus: Optional[str] = None

class SongCreate(SongBase):
    id: Optional[str] = None

class SongResponse(SongBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    chatInput: str
    targetLanguage: str

class PoetRequest(BaseModel):
    analysis: str
    bridge: str
    targetLanguage: str
    literalTranslation: str
    originalLyrics: str
    metaphors: str = ""

class EditorRequest(BaseModel):
    poetDraft: str
    structure: str
    mood: str
    targetLanguage: str

# --- Helper ---
async def call_llm(client: httpx.AsyncClient, model: str, prompt: str, temperature: float = 0.1) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = await client.post(BASE_URL, headers=headers, json=payload)
        if response.is_error:
            print(f"LLM API Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"CRITICAL Error calling LLM ({model}): {e}")
        return f"Error: {e}"

def extract_section(text: str, header: str) -> str:
    pattern = rf"\[{header}\](.*?)(?=\[|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match: return match.group(1).strip()
    pattern_fallback = rf"{header}:(.*?)(?={header}|[A-Z]+:|$)"
    match_fallback = re.search(pattern_fallback, text, re.DOTALL | re.IGNORECASE)
    if match_fallback: return match_fallback.group(1).strip()
    return ""

# --- Auth Helpers ---
def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_email = payload.get("sub")
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Song Endpoints ---
@app.get("/songs", response_model=List[SongResponse])
async def list_songs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Song).filter(Song.user_id == user.id).order_by(Song.updated_at.desc()).all()

@app.post("/songs", response_model=SongResponse)
async def save_song(req: SongCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if req.id:
        song = db.query(Song).filter(Song.id == req.id, Song.user_id == user.id).first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Update fields
        for key, value in req.dict(exclude={'id'}).items():
            setattr(song, key, value)
    else:
        song = Song(
            **req.dict(exclude={'id'}),
            user_id=user.id
        )
        db.add(song)
    
    db.commit()
    db.refresh(song)
    return song

@app.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    song = db.query(Song).filter(Song.id == song_id, Song.user_id == user.id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.delete("/songs/{song_id}")
async def delete_song(song_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    song = db.query(Song).filter(Song.id == song_id, Song.user_id == user.id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    db.delete(song)
    db.commit()
    return {"status": "deleted"}

# --- Auth Endpoints ---
@app.post("/register")
async def register_user(req: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == req.email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    new_user = User(first_name=req.first_name, last_name=req.last_name, email=req.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email, "user_id": new_user.id})
    return {"status": "success", "message": "User registered successfully", "access_token": access_token}

class UserLogin(BaseModel):
    email: EmailStr

@app.post("/login")
async def login_user(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
    
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    return {
        "status": "success",
        "message": "Login successful",
        "access_token": access_token
    }

@app.get("/auth/google")
async def auth_google(request: Request):
    redirect_uri = "http://127.0.0.1:5678/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    print(f"Auth Callback started. Session: {request.session}")
    try:
        token = await oauth.google.authorize_access_token(request)
        print("Token received successfully")
    except Exception as e:
        print(f"Google auth error: {e}")
        raise HTTPException(status_code=400, detail=f"Google auth error: {e}")
    
    user_info = token.get('userinfo')
    if not user_info:
        print("Failed to get user info")
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")
    
    email = user_info.get('email')
    print(f"User info received for email: {email}")
    google_id = user_info.get('sub')
    first_name = user_info.get('given_name', 'User')
    last_name = user_info.get('family_name', '')
    avatar_url = user_info.get('picture')

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, google_id=google_id, first_name=first_name, last_name=last_name, avatar_url=avatar_url)
        db.add(user)
    else:
        if not user.google_id: user.google_id = google_id
        user.avatar_url = avatar_url
    
    db.commit()
    db.refresh(user)

    # Create JWT
    jwt_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    # Safe cross-origin redirect passing token in URL, replacing history
    from fastapi.responses import HTMLResponse
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authenticating...</title>
    </head>
    <body>
        <script>
            window.location.replace('http://127.0.0.1:8080/index.html?token={jwt_token}');
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/me")
async def get_me(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    song_count = db.query(Song).filter(Song.user_id == user.id).count()
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "stats": {
            "total_songs": song_count
        }
    }

@app.put("/me")
async def update_me(req: UserUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if req.first_name: user.first_name = req.first_name
    if req.last_name: user.last_name = req.last_name
    db.commit()
    return {"status": "success", "message": "Profile updated successfully"}

# --- Webhooks ---
@app.post("/webhook/analyze-lyrics")
async def analyze_lyrics(req: AnalyzeRequest):
    model = "anthracite-org/magnum-v4-72b"
    
    prompt_analyzer = f"""SYSTEM: You are a precise linguistic and musical analyst. Analyze the provided lyrics in extreme detail. You MUST strictly divide your output into three sections with these exact headers:

[STRUCTURE]
Identify the poetic meter (стихотворный размер), number of feet, syllable count per line, and rhyme scheme.

[METAPHORS]
Extract and list the key metaphors, imagery, and poetic devices.

[HARMONY]
Suggest musical parameters that fit the mood and rhythm of these lyrics:
- KEY: (e.g., G Major or C# Minor)
- BPM: (e.g., 95)
- CHORDS VERSE: (e.g., Am - F - C - G)
- CHORDS CHORUS: (e.g., C - G - Am - F)

USER: Analyze this text:
{req.chatInput}"""

    prompt_bridge = f"SYSTEM: You are the Cultural Bridge and Translator. Analyze the lyrics and divide your output into two sections using these exact headers:\n\n[MOOD]\nSummarize the song's emotional payload, mood, and idioms.\n\n[TRANSLATION]\nProvide a literal, close-to-original semantic translation of the lyrics STRICTLY into {req.targetLanguage}. You MUST translate the full text.\n\nUSER: Analyze and translate into {req.targetLanguage}:\n{req.chatInput}"
    
    analyzer_task = call_llm(app.state.client, model, prompt_analyzer, 0.1)
    bridge_task = call_llm(app.state.client, model, prompt_bridge, 0.1)
    analysis_output, bridge_output = await asyncio.gather(analyzer_task, bridge_task)
    
    harmony_text = extract_section(analysis_output, "HARMONY")
    
    # Simple parser for structured harmony data
    def get_val(key, text):
        m = re.search(rf"{key}:\s*(.*)", text, re.I)
        return m.group(1).strip() if m else ""

    return {
        "structure_output": extract_section(analysis_output, "STRUCTURE") or analysis_output,
        "metaphors_output": extract_section(analysis_output, "METAPHORS") or "No metaphors found.",
        "mood_output": extract_section(bridge_output, "MOOD") or bridge_output,
        "poet_output": extract_section(bridge_output, "TRANSLATION") or bridge_output,
        "musical_data": {
            "key": get_val("KEY", harmony_text),
            "bpm": get_val("BPM", harmony_text),
            "chords_verse": get_val("CHORDS VERSE", harmony_text),
            "chords_chorus": get_val("CHORDS CHORUS", harmony_text)
        }
    }

@app.post("/webhook/poet-agent")
async def poet_agent(req: PoetRequest):
    model = "thedrummer/rocinante-12b"
    prompt = f"SYSTEM: You are Rocinante, a Master Songwriter. Your mission is to transform a literal translation into a SINGABLE poetic masterpiece in {req.targetLanguage}.\n\nUSER:\n[Original Lyrics]\n{req.originalLyrics}\n\n[Literal Translation]\n{req.literalTranslation}\n\n[Structure Analysis]\n{req.analysis}\n\n[Mood]\n{req.bridge}\n\nTASK: Write the final {req.targetLanguage} lyrics. No preamble, no comments. Output ONLY the song."
    poet_output = await call_llm(app.state.client, model, prompt, 0.3)
    return {"poet_output": poet_output}

@app.post("/webhook/literary-editor")
async def literary_editor(req: EditorRequest):
    model = "anthropic/claude-sonnet-4"
    prompt = f"SYSTEM: You are a Senior Literary Editor and Master Poet. Perform a FINAL SURGICAL POLISH on the draft.\nOutput ONLY the corrected song lyrics. No commentary.\n\nUSER: Polish this {req.targetLanguage} song draft:\n{req.poetDraft}"
    editor_output = await call_llm(app.state.client, model, prompt, 0.3)
    return {"editor_output": editor_output}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=5678, reload=False)
