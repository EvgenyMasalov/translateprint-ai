import httpx
import json
import os
import re
from datetime import datetime
from fastapi import HTTPException
from app.core.config import settings
from app.core.prompts import (
    LYRICS_ANALYSIS_PROMPT, HARMONY_ANALYSIS_PROMPT,
    DEEP_POLISH_PROMPT, POET_AGENT_PROMPT
)
import random

DEBUG_LOG_FILE = "ai_debug.log"

def log_debug(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

# Available Models (Verified with User Requirements and Polza AI)
MODELS = {
    "lyrics": "anthracite-org/magnum-v4-72b",          # Structure, Metaphors, Translated Output
    "harmony": "sao10k/l3.3-euryale-70b",               # Musical Harmony
    "agent_manuscript": "thedrummer/rocinante-12b",      # Agent: Analyze Manuscript
    "edited_results": "anthropic/claude-sonnet-4.6",    # Agent: Final Edited Results
    "fallback": "anthropic/claude-sonnet-4.6"           # High-stability fallback
}

async def call_llm(url: str, payload: dict):
    """Generic webhook caller (Legacy n8n path)"""
    log_debug(f"Calling Webhook at URL: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            if response.is_error:
                log_debug(f"Webhook Error ({response.status_code}): {response.text}")
                raise HTTPException(status_code=502, detail=f"LLM Provider Error: {response.status_code}")
            return response.json()
        except httpx.RequestError as exc:
            log_debug(f"Network error calling Webhook at {url}: {exc}")
            raise HTTPException(status_code=502, detail=f"Gateway error: {str(exc)}")

async def call_polza_ai(prompt: str, model: str, temperature: float = 0.1):
    """Direct call to Polza AI (OpenAI compatible)"""
    api_key = settings.POLZA_API_KEY.strip("<> ")
    if not api_key or "placeholder" in api_key:
        log_debug("Warning: POLZA_API_KEY missing or placeholder.")
        return None

    log_debug(f"--- START AI REQUEST ---")
    log_debug(f"Model: {model}, Temp: {temperature}")
    
    async with httpx.AsyncClient(timeout=300.0, trust_env=False) as client:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a specialized musical and poetic assistant. You MUST return your response as a valid JSON object ONLY. DO NOT use conversational text. ALL KEYS MUST BE IN ENGLISH."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 3000,
                "temperature": temperature
            }
            
            if "claude" in model or "gpt" in model:
                payload["response_format"] = { "type": "json_object" }
            
            response = await client.post(
                f"{settings.POLZA_BASE_URL}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.is_error:
                log_debug(f"ERROR from Polza AI ({response.status_code}): {response.text}")
                return None
                
            result = response.json()
            if 'choices' not in result or not result['choices']:
                return None

            content = result['choices'][0]['message']['content'].strip()
            log_debug(f"RAW CONTENT PREVIEW: {content[:100]}...")
            
            # --- GIBBERISH DETECTION ---
            weird_markers = ["╨", "╤", "тА", "╥Р", "╢"]
            weird_count = sum(content.count(m) for m in weird_markers)
            if weird_count > 50 or "KilledByNotEnoughNGrams" in content:
                log_debug("CRITICAL ERROR: Detected gibberish/corrupted output.")
                return None

            # JSON extraction
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            if not content.startswith("{"):
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    content = content[start:end+1]

            def repair_json(bad_json):
                fixed = bad_json.strip()
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass

                # Repair newlines and commas
                fixed = re.sub(r'("\s*)\n\s*("[\w_]+"\s*:)', r'\1,\n\2', fixed)
                fixed = fixed.replace('\\n', '[[_NL_]]').replace('\\"', '[[_Q_]]')
                fixed = fixed.replace('\n', '\\n').replace('\r', '')
                fixed = re.sub(r'\\n\s*([\{\}\[\]\:\,])', r'\1', fixed)
                fixed = re.sub(r'([\{\}\[\]\:\,])\s*\\n', r'\1', fixed)
                fixed = fixed.replace('[[_NL_]]', '\\n').replace('[[_Q_]]', '\\"')
                fixed = re.sub(r',\s*([\}\]])', r'\1', fixed)

                try:
                    return json.loads(fixed)
                except Exception:
                    schema_keys = ["poetDraft", "metaphors", "structure_output", "mood_output", "poet_output", "key", "bpm", "chords_verse", "chords_chorus", "editor_output"]
                    extracted = {}
                    for key in schema_keys:
                        m = re.search(f'"{key}"\\s*:\\s*"(.+?)"(?=\\s*,\\s*"|\\s*\\}})', fixed, re.DOTALL)
                        if m: extracted[key] = m.group(1).replace('\\n', '\n')
                    return extracted if extracted else None

            parsed = repair_json(content)
            if parsed:
                log_debug("JSON Parse: SUCCESS")
                return parsed
            
            log_debug("JSON Repair failed to produce valid object.")
            return None
            
        except Exception as exc:
            log_debug(f"CRITICAL ERROR in call_polza_ai: {exc}")
            return None
        finally:
            log_debug(f"--- END AI REQUEST ---")

async def analyze_lyrics_ai(chat_input: str, target_language: str):
    result = await call_polza_ai(LYRICS_ANALYSIS_PROMPT.format(lyrics=chat_input, target_language=target_language), MODELS["lyrics"])
    if not result:
        log_debug(f"RETRYING Lyrics Analysis with Fallback: {MODELS['fallback']}")
        result = await call_polza_ai(LYRICS_ANALYSIS_PROMPT.format(lyrics=chat_input, target_language=target_language), MODELS["fallback"])
    return result

async def analyze_harmony_ai(lyrics: str):
    return await call_polza_ai(HARMONY_ANALYSIS_PROMPT.format(lyrics=lyrics), MODELS["harmony"])

async def literary_editor_ai(poet_draft: str, structure: str, mood: str, target_language: str):
    return await call_polza_ai(DEEP_POLISH_PROMPT.format(poet_draft=poet_draft, structure=structure, mood=mood, target_language=target_language), MODELS["edited_results"])

async def poet_agent_ai(original_lyrics: str, analysis: str, metaphors: str, target_language: str, literal_translation: str):
    prompt = POET_AGENT_PROMPT.format(
        original_lyrics=original_lyrics,
        analysis=analysis,
        metaphors=metaphors,
        target_language=target_language,
        literal_translation=literal_translation
    )
    result = await call_polza_ai(prompt, MODELS["agent_manuscript"])
    if not result:
        log_debug(f"RETRYING Poet Agent with Fallback: {MODELS['fallback']}")
        result = await call_polza_ai(prompt, MODELS["fallback"])
    return result
