import httpx
import json
from fastapi import HTTPException
from app.core.config import settings
from app.core.prompts import (
    LYRICS_ANALYSIS_PROMPT, HARMONY_ANALYSIS_PROMPT,
    DEEP_POLISH_PROMPT, POET_AGENT_PROMPT
)
import random

# Available Models
MODELS = {
    "lyrics": "anthracite-org/magnum-v4-72b",
    "harmony": "sao10k/l3.3-euryale-70b",
    "editor_rocinante": "thedrummer/rocinante-12b",
    "editor_cydonia": "thedrummer/cydonia-24b-v4.1",
    "poet_master": "anthropic/claude-3.5-sonnet"
}

async def call_llm(url: str, payload: dict):
    """Generic webhook caller (Legacy n8n path)"""
    print(f"Calling Webhook at URL: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            if response.is_error:
                print(f"Webhook Error ({response.status_code}): {response.text}")
                raise HTTPException(status_code=502, detail=f"LLM Provider Error: {response.status_code}")
            return response.json()
        except httpx.RequestError as exc:
            print(f"Network error calling Webhook at {url}: {exc}")
            raise HTTPException(status_code=502, detail=f"Gateway error: {str(exc)}")

async def call_polza_ai(prompt: str, model: str = "gpt-4o"):
    """Direct call to Polza AI (OpenAI compatible)"""
    if not settings.POLZA_API_KEY or "placeholder" in settings.POLZA_API_KEY:
        print("Warning: POLZA_API_KEY missing or placeholder.")
        return None

    print(f"Calling Polza AI ({model}) at {settings.POLZA_BASE_URL}")
    
    # We use a very high timeout for AI responses
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            headers = {
                "Authorization": f"Bearer {settings.POLZA_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a specialized musical and poetic assistant. ALWAYS return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": { "type": "json_object" }
            }
            
            response = await client.post(
                f"{settings.POLZA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 407:
                print("Error: Proxy Authentication Required (407)")
                return None

            if response.is_error:
                print(f"Polza AI Error ({response.status_code}): {response.text}")
                return None
                
            result = response.json()
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
        except Exception as exc:
            print(f"Error calling Polza AI: {exc}")
            return None

async def analyze_lyrics_ai(chat_input: str, target_language: str):
    # Primarily use Magnum for lyrics analysis
    model = MODELS["lyrics"]
    prompt = LYRICS_ANALYSIS_PROMPT.format(lyrics=chat_input, target_language=target_language)
    return await call_polza_ai(prompt, model=model)

async def analyze_harmony_ai(lyrics: str):
    # Use Euryale for harmony suggestions
    model = MODELS["harmony"]
    prompt = HARMONY_ANALYSIS_PROMPT.format(lyrics=lyrics)
    return await call_polza_ai(prompt, model=model)

async def literary_editor_ai(poet_draft: str, structure: str, mood: str, target_language: str):
    # Randomly pick between Rocinante and Cydonia
    model = random.choice([MODELS["editor_rocinante"], MODELS["editor_cydonia"]])
    prompt = DEEP_POLISH_PROMPT.format(
        poet_draft=poet_draft,
        structure=structure,
        mood=mood,
        target_language=target_language
    )
    return await call_polza_ai(prompt, model=model)

async def poet_agent_ai(original_lyrics: str, analysis: str, metaphors: str, target_language: str):
    # Strict use of Claude Sonnet
    model = MODELS["poet_master"]
    prompt = POET_AGENT_PROMPT.format(
        original_lyrics=original_lyrics,
        analysis=analysis,
        metaphors=metaphors,
        target_language=target_language
    )
    return await call_polza_ai(prompt, model=model)
