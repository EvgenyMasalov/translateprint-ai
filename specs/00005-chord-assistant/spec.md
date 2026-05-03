---
spec_type: product
spec_maturity: draft
---

# Problem Statement
LyricAI Studio currently focuses entirely on the textual and linguistic aspects of songwriting. However, lyrics are only half of a song. Songwriters often struggle to find the right musical mood, chord progressions, and tempo that complement their lyrics. Adding an AI Chord Assistant will provide a bridge between poetry and music, helping creators jumpstart their composition process.

# Scope

## Included
- **Music Analysis Module**: AI logic to suggest chords, key, and tempo based on the analyzed lyrics and mood.
- **New Sidebar Card**: A "Musical Harmony" card in the Actionable Insights panel.
- **Chord Progressions**: Suggestions for specific song parts (Verse, Chorus, Bridge).
- **Musical Style Tags**: Suggestions for genre, BPM, and instrumentation.
- **Database Storage**: Saving musical suggestions along with the song project.
- **PDF Export**: Inclusion of musical suggestions in the professional report.

## Excluded
- **Audio Playback**: Playing the actual chords or melodies (out of scope for this version).
- **Sheet Music Generation**: Generating formal musical notation.
- **Instrument-specific Tabs**: Detailed guitar tabs or piano fingerings.

## Edge Cases & Boundaries
- **Abstract Lyrics**: Handling cases where the mood is ambiguous.
- **Instrument Choice**: Recommendations might vary based on whether the user plays guitar vs piano.

# User Scenarios & Testing

## [US1] Getting Musical Inspiration
- **Description**: As a songwriter, I want to see what chords would fit my new lyrics.
- **Acceptance Scenario**:
    - **Given**: I have entered lyrics about a "lonely rainy city".
    - **When**: I click "Analyze".
    - **Then**: The "Musical Harmony" card displays a suggested key (e.g., A Minor) and a moody chord progression.

## [US2] Saving Harmony with the Song
- **Description**: As a user, I want my musical ideas to be saved along with my lyrics.
- **Acceptance Scenario**:
    - **Given**: I have received chord suggestions for my song.
    - **When**: I save the song to the library.
    - **Then**: When I reload the song, the same chord suggestions appear.

# Requirements

## Functional Requirements
- **FR-001**: System MUST suggest at least one chord progression for the lyrics.
- **FR-002**: System MUST suggest a musical key and tempo (BPM).
- **FR-003**: Musical suggestions MUST be visible in the Actionable Insights panel.
- **FR-004**: Musical data MUST be included in the PDF export.

## Technical Requirements
- **TR-001**: Update the backend `AnalyzeRequest` to include a musical analysis prompt.
- **TR-002**: Extend the `Song` database model to store harmony data.
- **TR-003**: Ensure the LLM output for chords is parsed and displayed cleanly.

# Key Entities
- **HarmonyData**: { key, tempo, genre, progression_verse, progression_chorus }

# Success Criteria
- **SC-001**: User receives musical suggestions that align with the detected mood of the lyrics.
- **SC-002**: Suggestions are persisted in the database and restored correctly.
- **SC-003**: The UI remains clean and "Musical Harmony" fits into the existing sidebar.

## Compliance Check
*(Pending Policy Auditor)*
