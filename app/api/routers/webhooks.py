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

async def get_mock_response(payload: dict):
    # Simulate different responses based on payload structure
    if "chatInput" in payload:
        # Lyrics analysis (Match editor.js expectations)
        return {
            "structure_output": "Verse 1: 4 lines, AABB rhyme scheme\nChorus: Catchy and repetitive\nVerse 2: Story development (MOCK)",
            "mood_output": "Melancholic but hopeful emotional payload (MOCK)",
            "metaphors_output": "Lonely cloud, withered rose of time (MOCK)",
            "poet_output": f"Masterpiece draft in {payload.get('targetLanguage', 'English')} (MOCK):\n\nSky is grey, heart is heavy,\nBut the morning light is ready.",
            "musical_data": {
                "key": "G Major",
                "bpm": "115",
                "chords_verse": "G | C | D | G",
                "chords_chorus": "C | D | Em | C"
            }
        }
    elif "analysis" in payload and "originalLyrics" in payload:
        # Poet agent
        return {
            "poetDraft": "Refined lyrics draft with better flow (MOCK)",
            "metaphors": "Enhanced metaphors about time (MOCK)"
        }
    elif "poetDraft" in payload:
        # Literary editor (Match agent-ui.js expectations)
        return {
            "editor_output": "Polished by AI (MOCK): This version has improved rhythm and rhyme while preserving your original intent.",
            "structure": "Verse-Chorus-Verse-Bridge-Chorus"
        }
    elif "lyrics" in payload:
        # Harmony analysis (Match agent-ui.js expectations)
        return {
            "key": "C Major",
            "bpm": "120",
            "chords_verse": "C | F | G | C",
            "chords_chorus": "Am | F | C | G"
        }
    return {"message": "Mock response", "payload": payload}

@router.post("/webhook/analyze-lyrics")
async def analyze_lyrics(req: WebhookLyricsRequest):
    # Try Real AI first
    result = await analyze_lyrics_ai(req.chatInput, req.targetLanguage)
    if result:
        return result
        
    # Fallback to Webhook if configured and not mock
    if "mock-webhook" not in settings.N8N_ANALYZE_LYRICS_URL:
        try:
            return await call_llm(settings.N8N_ANALYZE_LYRICS_URL, req.dict())
        except:
            pass
            
    # Final fallback to Mock
    return await get_mock_response(req.dict())

@router.post("/webhook/analyze-harmony")
async def analyze_harmony(req: WebhookHarmonyRequest):
    result = await analyze_harmony_ai(req.lyrics)
    if result:
        return result
        
    if "mock-webhook" not in settings.N8N_ANALYZE_HARMONY_URL:
        try:
            return await call_llm(settings.N8N_ANALYZE_HARMONY_URL, req.dict())
        except:
            pass
            
    return await get_mock_response(req.dict())

@router.post("/webhook/poet-agent")
async def poet_agent(req: WebhookPoetRequest):
    result = await poet_agent_ai(
        req.originalLyrics, req.analysis, 
        req.metaphors, req.targetLanguage
    )
    if result:
        return result
        
    if "mock-webhook" not in settings.N8N_POET_AGENT_URL:
        try:
            return await call_llm(settings.N8N_POET_AGENT_URL, req.dict())
        except:
            pass
            
    return await get_mock_response(req.dict())

@router.post("/webhook/literary-editor")
async def literary_editor(req: WebhookEditorRequest):
    result = await literary_editor_ai(
        req.poetDraft, req.structure, 
        req.mood, req.targetLanguage
    )
    if result:
        return result
        
    if "mock-webhook" not in settings.N8N_LITERARY_EDITOR_URL:
        try:
            return await call_llm(settings.N8N_LITERARY_EDITOR_URL, req.dict())
        except:
            pass
            
    return await get_mock_response(req.dict())

@router.post("/mock-webhook")
async def mock_webhook(request: Request):
    payload = await request.json()
    return await get_mock_response(payload)
