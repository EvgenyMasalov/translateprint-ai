import asyncio
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="LyricAI Studio Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "pza_G_FZmM7EG9hndBPr_aDBU-aErTxCgJnm"
BASE_URL = "https://polza.ai/api/v1/chat/completions"

# --- Models ---
class AnalyzeRequest(BaseModel):
    chatInput: str
    targetLanguage: str

class PoetRequest(BaseModel):
    analysis: str
    bridge: str
    targetLanguage: str
    literalTranslation: str
    originalLyrics: str

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
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = await client.post(BASE_URL, headers=headers, json=payload, timeout=120.0)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM ({model}): {e}")
        return f"Error: {e}"

# --- Webhooks ---
@app.post("/webhook/analyze-lyrics")
async def analyze_lyrics(req: AnalyzeRequest):
    model = "anthracite-org/magnum-v4-72b"
    
    prompt_analyzer = f"""SYSTEM: You are a precise linguistic analyst. Analyze the provided lyrics in extreme detail. You MUST strictly divide your output into two sections with these exact headers:

[STRUCTURE]
Identify the poetic meter (стихотворный размер, e.g., iambic, trochaic), the number of feet (количество стоп), the syllable count per line, and the rhyme scheme. Be precise and analytical.

[METAPHORS]
Extract and list the key metaphors, imagery, and poetic devices found in the text.

USER: Analyze this text:
{req.chatInput}"""

    prompt_bridge = f"""SYSTEM: You are the Cultural Bridge and Translator. Analyze the lyrics and divide your output into two sections using these exact headers:

[MOOD]
Summarize the song's emotional payload, mood, and idioms.

[TRANSLATION]
Provide a literal, close-to-original semantic translation of the lyrics STRICTLY into {req.targetLanguage}. You MUST translate the full text.

USER: Analyze and translate into {req.targetLanguage}:
{req.chatInput}"""

    async with httpx.AsyncClient() as client:
        # Run both analysis and bridge requests concurrently
        analyzer_task = call_llm(client, model, prompt_analyzer, 0.1)
        bridge_task = call_llm(client, model, prompt_bridge, 0.1)
        analysis_output, bridge_output = await asyncio.gather(analyzer_task, bridge_task)

    # Parse Analyzer Output
    structure = analysis_output
    metaphors = "No metaphors found."
    meta_idx = analysis_output.find("[METAPHORS]")
    if meta_idx != -1:
        structure = analysis_output[:meta_idx].replace("[STRUCTURE]", "").strip()
        metaphors = analysis_output[meta_idx:].replace("[METAPHORS]", "").strip()
    elif "METAPHORS:" in analysis_output:
        parts = analysis_output.split("METAPHORS:")
        structure = parts[0].replace("STRUCTURE:", "").strip()
        metaphors = parts[1].strip()

    # Parse Bridge Output
    mood = bridge_output
    translation = bridge_output
    trans_idx = bridge_output.find("[TRANSLATION]")
    if trans_idx != -1:
        mood = bridge_output[:trans_idx].replace("[MOOD]", "").strip()
        translation = bridge_output[trans_idx:].replace("[TRANSLATION]", "").strip()

    return {
        "structure_output": structure,
        "metaphors_output": metaphors,
        "mood_output": mood,
        "poet_output": translation
    }

@app.post("/webhook/poet-agent")
async def poet_agent(req: PoetRequest):
    model = "thedrummer/rocinante-12b"
    prompt = f"""SYSTEM: You are Rocinante, a brilliant rock/pop songwriter. Craft final {req.targetLanguage} lyrics based on the emotional payload. Respect the syllable structure and keep the vibe authentic to {req.targetLanguage}.

USER: Write {req.targetLanguage} song lyrics.
Structure:
{req.analysis}

Emotional meaning:
{req.bridge}"""

    async with httpx.AsyncClient() as client:
        poet_output = await call_llm(client, model, prompt, 0.3)

    return {"poet_output": poet_output}

@app.post("/webhook/literary-editor")
async def literary_editor(req: EditorRequest):
    model = "anthropic/claude-sonnet-4"
    prompt = f"""SYSTEM: You are a Senior Literary Editor and Master Poet with decades of experience in songwriting across all genres and languages. Your task is to perform a FINAL SURGICAL POLISH on an already-crafted song translation.

CRITICAL CONSTRAINTS:
1. You MUST NOT alter the core meaning, emotional intent, or narrative arc of the text. The song's soul is sacred.
2. You MUST preserve the existing syllable structure and rhythmic pattern as closely as possible.
3. You may ONLY make the following types of corrections:
   - Replace awkward or unnatural word choices with more elegant, singable alternatives
   - Fix grammatical issues while keeping the poetic register
   - Improve internal rhyme quality and consonance where it doesn't sacrifice meaning
   - Smooth transitions between verses for better vocal flow
   - Ensure cultural authenticity of idioms and expressions in {req.targetLanguage}
4. Output ONLY the corrected song lyrics. No commentary, no explanations, no annotations.
5. If the text is already excellent, return it unchanged. Do NOT change things for the sake of changing them.

STRUCTURAL REFERENCE (for rhythmic guidance):
{req.structure}

EMOTIONAL REFERENCE (mood to preserve):
{req.mood}

USER: Polish this {req.targetLanguage} song draft. Return ONLY the final lyrics:
{req.poetDraft}"""

    async with httpx.AsyncClient() as client:
        editor_output = await call_llm(client, model, prompt, 0.3)

    return {"editor_output": editor_output}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=5678, reload=False)
