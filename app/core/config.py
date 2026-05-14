from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "LyricAI Studio"
    API_V1_STR: str = "/api/v1"
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "placeholder-secret-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./users.db")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://127.0.0.1:8080")
    
    # AI Services
    POLZA_API_KEY: str = os.getenv("POLZA_API_KEY", "pza_G_FZmM7EG9hndBPr_aDBU-aErTxCgJnm")
    POLZA_BASE_URL: str = os.getenv("POLZA_BASE_URL", "https://polza.ai/api/v1")
    
    # LLM Webhooks
    N8N_ANALYZE_LYRICS_URL: str = os.getenv("N8N_ANALYZE_LYRICS_URL", "https://your-n8n.instance/webhook/analyze-lyrics")
    N8N_POET_AGENT_URL: str = os.getenv("N8N_POET_AGENT_URL", "https://your-n8n.instance/webhook/poet-agent")
    N8N_LITERARY_EDITOR_URL: str = os.getenv("N8N_LITERARY_EDITOR_URL", "https://your-n8n.instance/webhook/literary-editor")
    N8N_ANALYZE_HARMONY_URL: str = os.getenv("N8N_ANALYZE_HARMONY_URL", "https://your-n8n.instance/webhook/analyze-harmony")

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

settings = Settings()
