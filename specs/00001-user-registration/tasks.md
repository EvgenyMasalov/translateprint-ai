# Tasks: User Registration & Google OAuth2

**Project Mode**: Brownfield

## Phase 1: Setup & Foundations
- [X] T001 Install dependencies (SQLAlchemy, Authlib, PyJWT) in requirements.txt
- [X] T002 Update .env.example with GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and JWT_SECRET
- [X] T003 {TR-002} Create database setup and User model in database.py → exports: User, init_db()

## Phase 2: Delivery — Manual Registration [US1] 🎯 MVP
- [X] T004 [P] [US1] {FR-003,TR-003} Implement JWT helper functions in auth_utils.py → exports: create_token()
- [X] T005 [US1] {FR-001,FR-002} Create registration page registration.html with Tailwind CSS
- [X] T006 [US1] {TR-001,FR-005} Implement POST /register endpoint in backend.py after:T003 ← T003:User, T004:create_token()
- [X] T007 [US1] {FR-001,FR-002} [COMPLETES FR-001] Implement form submission logic in registration.html ← T006

## Phase 3: Delivery — Google OAuth2 [US2] 🎯 MVP
- [X] T008 [US2] {FR-004} Configure Authlib OAuth client for Google in backend.py
- [X] T009 [US2] {FR-004,TR-004} Implement GET /auth/google (login start) in backend.py
- [X] T010 [US2] {FR-004,TR-004} Implement GET /auth/google/callback in backend.py after:T003 ← T003:User
- [X] T011 [US2] {FR-004} [COMPLETES FR-004] Add "Sign in with Google" button to registration.html

## Phase 4: Delivery — Integration & Profile [US3]
- [X] T012 [US3] {TR-001} Implement GET /me (current user info) in backend.py ← T003:User
- [X] T013 [US3] {FR-001} Add Account/Login icon to header in index.html and redirect logic
- [X] T014 [US3] {FR-001} [COMPLETES FR-001] Implement logout and session check logic in index.html

## Phase 5: Polish
- [X] T015 Verify error handling for email collisions and OAuth failures
- [X] T016 Add basic unit tests for User model in tests/test_database.py after:T003
