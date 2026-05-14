from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db_session import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.database_models import User
from app.models.schemas import UserRegister, Token, UserUpdate, UserResponse, UserLogin
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(req: UserRegister, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == req.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        hashed_password=get_password_hash(req.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(subject=new_user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_user(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    if not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from app.models.database_models import Song
    song_count = db.query(Song).filter(Song.user_id == current_user.id).count()
    
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "contribution_level": current_user.contribution_level,
        "stats": {
            "total_songs": song_count
        }
    }

@router.put("/me", response_model=UserResponse)
async def update_user_me(req: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.first_name is not None:
        current_user.first_name = req.first_name
    if req.last_name is not None:
        current_user.last_name = req.last_name
    
    db.commit()
    db.refresh(current_user)
    
    from app.models.database_models import Song
    song_count = db.query(Song).filter(Song.user_id == current_user.id).count()
    
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "contribution_level": current_user.contribution_level,
        "stats": {
            "total_songs": song_count
        }
    }
