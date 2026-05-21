# Implementation Plan: MVP Monetization

## Phase 1: Research & Preparation
-   [x] Analyze current header structure in `index.html`.
-   [x] Identify auth state handling in frontend.
-   [x] Design the "Donate" button style.

## Phase 2: Frontend Implementation
-   [x] Add the "Donate" button to `index.html` header.
-   [x] Implement visibility logic (show only if `lyricai_token` exists).
-   [x] Create the Monetization Modal (Donation Modal).
-   [x] Add "fake" payment flow (loading state -> success message).

## Phase 3: Backend Integration (Fake)
-   [x] Add a `/monetize/donate` endpoint in `backend.py`.
-   [x] Update User model to include a `contribution_level` field.

## Phase 4: Validation
-   [x] Verify the button appears only after login.
-   [x] Test the modal interaction.
-   [x] Ensure UI consistency in both light and dark modes.
