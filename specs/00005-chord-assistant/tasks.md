# Tasks: AI Chord Assistant

**Project Mode**: Brownfield

## Phase 1: Data Infrastructure
- [X] T001 {TR-002} Add `musical_key`, `bpm`, `chords_verse`, and `chords_chorus` columns to `Song` model in `database.py`
- [X] T002 Update `SongBase` and `SongResponse` schemas in `backend.py` to include new musical fields

## Phase 2: AI Analysis Extension
- [X] T003 {TR-001} Update `analyze_lyrics` prompt in `backend.py` to request musical data (Key, BPM, Chords) using `[HARMONY]` tag
- [X] T004 {TR-003} Implement parsing for the `[HARMONY]` section in `backend.py`
- [X] T005 Update `AnalyzeRequest` and response logic to return structured musical data to the frontend

## Phase 3: Frontend — Musical Harmony UI
- [X] T006 {FR-003} Create "Musical Harmony" card HTML/CSS in `index.html` (monospaced chords, BPM badge)
- [X] T007 Implement JS logic in `index.html` to display musical data after analysis
- [X] T008 Update `loadSong` and `saveSong` in `index.html` to handle the new musical fields

## Phase 4: Reporting & Export
- [X] T009 {FR-004} Update `pdf-template` in `index.html` to include a "Musical Harmony" section
- [X] T010 Update `generatePDF()` in `index.html` to populate the musical fields into the PDF
- [X] T011 (Optional) Sync musical data to `agent.html` for comprehensive PDF reports from both pages

## Phase 5: Polish & Validation
- [X] T012 Verify that chord suggestions align with different lyric moods (e.g., Sad -> Minor keys, Happy -> Major keys)
- [X] T013 Ensure BPM is within a reasonable range (40-200)
- [X] T014 Manual QA: Perform full flow (Write -> Analyze -> View Chords -> Save -> Export PDF)
