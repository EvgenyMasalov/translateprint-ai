import asyncio
import httpx
import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("POLZA_API_KEY", "your_api_key_here")
BASE_URL = "https://polza.ai/api/v1/chat/completions"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize a single httpx client for the entire app lifetime
    # trust_env=False prevents picking up system proxy settings that might require auth (Error 407)
    app.state.client = httpx.AsyncClient(timeout=120.0, trust_env=False)
    yield
    await app.state.client.aclose()

app = FastAPI(title="LyricAI Studio Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    metaphors: str = "" # Optional field for metaphors

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
        response = await client.post(BASE_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling LLM ({model}): {e}")
        return f"Error: {e}"

def extract_section(text: str, header: str) -> str:
    """Helper to extract sections using regex for better robustness."""
    pattern = rf"\[{header}\](.*?)(?=\[|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    
    # Fallback for "HEADER:" format
    pattern_fallback = rf"{header}:(.*?)(?={header}|[A-Z]+:|$)"
    match_fallback = re.search(pattern_fallback, text, re.DOTALL | re.IGNORECASE)
    if match_fallback:
        return match_fallback.group(1).strip()
    
    return ""

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

    # Run both analysis and bridge requests concurrently
    analyzer_task = call_llm(app.state.client, model, prompt_analyzer, 0.1)
    bridge_task = call_llm(app.state.client, model, prompt_bridge, 0.1)
    analysis_output, bridge_output = await asyncio.gather(analyzer_task, bridge_task)

    # Robust parsing
    structure = extract_section(analysis_output, "STRUCTURE") or analysis_output
    metaphors = extract_section(analysis_output, "METAPHORS") or "No metaphors found."
    mood = extract_section(bridge_output, "MOOD") or bridge_output
    translation = extract_section(bridge_output, "TRANSLATION") or bridge_output

    return {
        "structure_output": structure,
        "metaphors_output": metaphors,
        "mood_output": mood,
        "poet_output": translation
    }

@app.post("/webhook/poet-agent")
async def poet_agent(req: PoetRequest):
    model = "thedrummer/rocinante-12b"
    # Added explicit requirement to use analyzed metaphors and mood
    prompt = f"""SYSTEM: You are Rocinante, a Master Songwriter. Your mission is to transform a literal translation into a SINGABLE poetic masterpiece in {req.targetLanguage}.

CRITICAL REQUIREMENTS:
1. STRICT ADHERENCE TO CONTENT: You MUST preserve every nuance of meaning from the [Literal Translation].
2. RHYTHMIC INTEGRITY: Use the [Structure Analysis] as a rigid blueprint for syllable counts and meter.
3. IMAGERY: Incorporate the specific [Key Metaphors] identified in the analysis.
4. EMOTIONAL TONE: Maintain the exact [Mood] described below.

USER:
[Original Lyrics]
{req.originalLyrics}

[Literal Translation]
{req.literalTranslation}

[Structure Analysis]
{req.analysis}

[Mood]
{req.bridge}

TASK: Write the final {req.targetLanguage} lyrics. No preamble, no comments. Output ONLY the song."""

    poet_output = await call_llm(app.state.client, model, prompt, 0.3)

    return {"poet_output": poet_output}

@app.post("/webhook/literary-editor")
async def literary_editor(req: EditorRequest):
    model = "anthropic/claude-sonnet-4"
    prompt = f"""SYSTEM: You are a Senior Literary Editor and Master Poet. Perform a FINAL SURGICAL POLISH on the draft.
Output ONLY the corrected song lyrics. No commentary.

CRITICAL CONSTRAINTS:
1. Preserve core meaning and emotional intent.
2. Maintain syllable structure and rhythm.
3. Improve singability and cultural authenticity in {req.targetLanguage}.

STRUCTURAL REFERENCE:
{req.structure}

EMOTIONAL REFERENCE:
{req.mood}

USER: Polish this {req.targetLanguage} song draft:
{req.poetDraft}"""

    editor_output = await call_llm(app.state.client, model, prompt, 0.3)

    return {"editor_output": editor_output}

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=5678, reload=False)
