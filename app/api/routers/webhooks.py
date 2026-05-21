from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.schemas import (
    WebhookLyricsRequest, WebhookHarmonyRequest, 
    WebhookPoetRequest, WebhookEditorRequest
)
from app.services.llm import (
    call_llm, analyze_lyrics_ai, analyze_harmony_ai,
    literary_editor_ai, poet_agent_ai
)
from app.core.config import settings

router = APIRouter()

@router.post("/webhook/analyze-lyrics")
async def analyze_lyrics(req: WebhookLyricsRequest):
    print(f"STRICT: Analyzing lyrics with real AI (Magnum)...")
    result = await analyze_lyrics_ai(req.chatInput, req.targetLanguage)
    if not result:
        raise HTTPException(status_code=502, detail="AI Provider failed to return valid analysis. Check backend logs.")
    return result

@router.post("/webhook/analyze-harmony")
async def analyze_harmony(req: WebhookHarmonyRequest):
    print(f"STRICT: Analyzing harmony with real AI (Euryale)...")
    result = await analyze_harmony_ai(req.lyrics)
    if not result:
        raise HTTPException(status_code=502, detail="AI Provider failed to return harmony data.")
    return result

@router.post("/webhook/poet-agent")
async def poet_agent(req: WebhookPoetRequest):
    print(f"STRICT: Poet Agent call (Rocinante)...")
    result = await poet_agent_ai(
        req.originalLyrics, req.analysis, 
        req.metaphors, req.targetLanguage,
        req.literalTranslation
    )
    if not result:
        raise HTTPException(status_code=502, detail="AI Provider failed in Poet Agent phase.")
    return result

@router.post("/webhook/literary-editor")
async def literary_editor(req: WebhookEditorRequest):
    print(f"STRICT: Literary Editor call (Claude)...")
    result = await literary_editor_ai(
        req.poetDraft, req.structure, 
        req.mood, req.targetLanguage
    )
    if not result:
        raise HTTPException(status_code=502, detail="AI Provider failed in Literary Editor phase.")
    return result

@router.post("/mock-webhook")
async def mock_webhook(request: Request):
    raise HTTPException(status_code=403, detail="Mocking is disabled.")
