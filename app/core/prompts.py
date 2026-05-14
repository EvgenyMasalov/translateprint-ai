# app/core/prompts.py

LYRICS_ANALYSIS_PROMPT = """
You are a professional songwriting assistant. Analyze the following lyrics and provide:
1. Structural analysis (Verse, Chorus, Bridge, etc.)
2. Emotional mood and payload.
3. Key metaphors and poetic devices used.
4. A poetic translation or adaptation into {target_language}.

[LYRICS]
{lyrics}

Return your response in structured JSON format with keys:
"structure_output", "mood_output", "metaphors_output", "poet_output".
"""

HARMONY_ANALYSIS_PROMPT = """
You are a professional music producer. Based on these lyrics, suggest:
1. Musical key (e.g., G Major).
2. Recommended BPM.
3. Chords for Verse.
4. Chords for Chorus.

[LYRICS]
{lyrics}

[HARMONY]
Return your response in structured JSON format with keys:
"key", "bpm", "chords_verse", "chords_chorus".
"""

DEEP_POLISH_PROMPT = """
You are a master literary editor. Refine the following poetic draft.
Preserve the intent, but improve rhythm, rhyme, and emotional impact.
Target Language: {target_language}
Original Mood: {mood}
Original Structure: {structure}

[DRAFT]
{poet_draft}

Return your response in structured JSON format with keys:
"editor_output", "structure".
"""

POET_AGENT_PROMPT = """
You are an expert songwriter. Given the analysis and literal translation, create a masterpiece draft.
Original Lyrics: {original_lyrics}
Analysis: {analysis}
Metaphors: {metaphors}
Target Language: {target_language}

[MASTERPIECE]
Return your response in structured JSON format with keys:
"poetDraft", "metaphors".
"""
