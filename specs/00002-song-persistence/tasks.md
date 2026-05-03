# Tasks: Song Persistence

**Project Mode**: Brownfield

## Phase 1: Foundations
- [X] T001 {TR-001} Update database.py with Song model and User relationship → exports: Song
- [X] T002 Update backend.py imports and add Pydantic schemas for Song (Create/Update/Response)

## Phase 2: Backend API Delivery [US1, US2, US3] 🎯 MVP
- [X] T003 [US2] {TR-002} Implement GET /songs endpoint to list user projects in backend.py after:T001
- [X] T004 [US1] {FR-001,FR-005} Implement POST /songs endpoint (create/upsert) in backend.py after:T001 ← T001:Song
- [X] T005 [US3] {FR-003} Implement GET /songs/{id} endpoint to retrieve full song data in backend.py after:T001
- [X] T006 {FR-004} Implement DELETE /songs/{id} endpoint in backend.py after:T001

## Phase 3: Frontend UI — Song Library [US2, US3] 🎯 MVP
- [X] T007 [US2] {FR-003} Add sidebar HTML/CSS to index.html for the song library list
- [X] T008 [US2] {FR-003} Implement JS logic to fetch and render the list of songs in sidebar
- [X] T009 [US3] {FR-003} Implement JS logic to load a selected song into editor and analysis cards ← T008

## Phase 4: Integration & Persistence [US1]
- [X] T010 [US1] {FR-005} [COMPLETES FR-005] Update analysis logic in index.html to auto-save results to backend after:T004
- [X] T011 [US1] {FR-001} Add "New Song" and "Save Now" buttons to the editor header in index.html
- [X] T012 {FR-004} Implement "Delete" button logic in the sidebar with confirmation dialog

## Phase 5: Polish & UX
- [X] T013 Improve sidebar UX with slide-in animations and loading states
- [X] T014 Ensure proper error handling for expired JWT or missing songs in frontend
- [X] T015 Verify that guest users are prompted to login before saving projects
