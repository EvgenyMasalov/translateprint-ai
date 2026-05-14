from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.db_session import get_db
from app.models.database_models import Song, User
from app.models.schemas import SongCreate, SongResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/songs", response_model=List[SongResponse])
async def list_songs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Song).filter(Song.user_id == current_user.id).order_by(Song.updated_at.desc()).all()

@router.post("/songs", response_model=SongResponse)
async def create_or_update_song(req: SongCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    song = None
    if req.id:
        song = db.query(Song).filter(Song.id == req.id, Song.user_id == current_user.id).first()
    
    if song:
        # Update existing
        for key, value in req.dict(exclude_unset=True).items():
            setattr(song, key, value)
    else:
        # Create new
        song = Song(
            **req.dict(exclude={"id"}),
            user_id=current_user.id
        )
        if req.id: song.id = req.id
        db.add(song)
    
    db.commit()
    db.refresh(song)
    return song

@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(song_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id, Song.user_id == current_user.id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.delete("/songs/{song_id}")
async def delete_song(song_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    song = db.query(Song).filter(Song.id == song_id, Song.user_id == current_user.id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    
    db.delete(song)
    db.commit()
    return {"status": "deleted"}
