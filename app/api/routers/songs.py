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
    print(f"DEBUG: Save Song Request - Title: {req.title}, ID: {req.id}")
    try:
        song = None
        if req.id:
            song = db.query(Song).filter(Song.id == req.id, Song.user_id == current_user.id).first()
        
        if song:
            # Update existing
            print(f"DEBUG: Updating existing song: {song.id}")
            update_data = req.dict(exclude_unset=True, exclude={"id"})
            for key, value in update_data.items():
                setattr(song, key, value)
        else:
            # Create new
            print("DEBUG: Creating new song")
            song_data = req.dict(exclude={"id"})
            song = Song(
                **song_data,
                user_id=current_user.id
            )
            # If a specific ID was requested and it's not "null"/"undefined"
            if req.id and req.id not in ["null", "undefined"]:
                song.id = req.id
            db.add(song)
        
        db.commit()
        db.refresh(song)
        print(f"DEBUG: Song saved successfully: {song.id}")
        return song
    except Exception as e:
        print(f"ERROR saving song: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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
