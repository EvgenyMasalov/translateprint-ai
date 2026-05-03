# Tasks: User Profile & Settings

**Project Mode**: Brownfield

## Phase 1: Backend API Delivery [US1, US2] 🎯 MVP
- [X] T001 Update `backend.py` with `UserUpdate` Pydantic schema (first_name, last_name)
- [X] T002 Implement `PUT /me` endpoint in `backend.py` to update user information
- [X] T003 Update `GET /me` endpoint in `backend.py` to include `stats` (count of songs from DB)

## Phase 2: Frontend — Profile UI [US1, US2] 🎯 MVP
- [X] T004 Add Profile Modal HTML/CSS to `index.html` (form for name, display stats)
- [X] T005 Implement JS logic in `index.html` to open modal from avatar and handle name updates
- [X] T006 Synchronize avatar and name display in header after profile update

## Phase 3: Dark Mode Delivery [US3]
- [X] T007 Implement shared theme detection and application logic in `index.html` and `agent.html`
- [X] T008 Add Dark Mode toggle switch to the Profile Modal
- [X] T009 Verify Tailwind `dark:` variants coverage for main UI components (Editor, Cards, Sidebar)

## Phase 4: Cross-Page Integration
- [X] T010 Synchronize Profile Modal and theme logic in `agent.html` (parity with `index.html`)
- [X] T011 Add logout button to Profile Modal (improves discoverability)

## Phase 5: Polish & Validation
- [X] T012 Add manual test cases for name validation (empty strings, length limits)
- [X] T013 Verify theme persistence across full page reloads and tab switching
- [X] T014 Ensure profile stats update immediately after saving a new song
