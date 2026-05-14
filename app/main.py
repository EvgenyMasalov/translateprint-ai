from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.routers import auth, songs, webhooks, monetize
from app.core.config import settings
from app.core.db_session import engine, Base
from contextlib import asynccontextmanager
from datetime import datetime, timezone

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create DB tables on startup
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Manual CORS Middleware (Extreme reliability)
@app.middleware("http")
async def custom_cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response()
    else:
        response = await call_next(request)
    
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
        
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response

# Add Session Middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

# Routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(songs.router, tags=["Songs"])
app.include_router(webhooks.router, tags=["Webhooks"])
app.include_router(monetize.router, tags=["Monetization"])

@app.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    Base.metadata.create_all(bind=engine)
    uvicorn.run("app.main:app", host="0.0.0.0", port=5678, reload=True)
