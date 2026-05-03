---
spec_type: product
spec_maturity: draft
---

# Problem Statement
Currently, LyricAI Studio lacks a user management system. Users cannot save their lyrics, analysis history, or preferences across sessions. This limits the application's utility as a professional workspace. Adding a registration system with Google Authentication will allow users to securely create accounts and pave the way for future persistent features.

# Scope

## Included
- **Registration Page**: A dedicated page (`registration.html`) with a form for manual registration.
- **Registration Form**: Fields for User Name, Last Name, and E-mail.
- **Google Authentication**: Integration with Google OAuth2 for one-click registration and login.
- **Entry Point**: A new icon in the main header to access the registration/login page.
- **User Storage**: Backend logic to store user data in a local database (SQLite).
- **Session Management**: JWT-based authentication to keep users logged in.

## Excluded
- **Password Reset**: Manual password recovery via email (will use Google Auth as primary secure method for now).
- **Profile Management**: Updating user details after registration.
- **Admin Dashboard**: User management for administrators.

## Edge Cases & Boundaries
- **Email Collision**: A user tries to register with an email that already exists.
- **Google Auth Email Match**: A user logs in via Google with an email already registered manually.
- **Network Failures**: Handling cases where Google APIs are unreachable.

# User Scenarios & Testing

## [US1] Manual User Registration
- **Description**: As a new user, I want to register using my name and email so I can create an account.
- **Priority**: P1 (Critical)
- **Rationale**: Core requirement for user identity.
- **One-sentence Test**: User fills the form, submits, and is redirected to the editor with a success message.
- **Acceptance Scenario**:
    - **Given**: I am on the registration page.
    - **When**: I enter "John", "Doe", and "john.doe@example.com" and click "Register".
    - **Then**: An account is created in the database, and I am logged in.

## [US2] Registration via Google
- **Description**: As a new user, I want to register using my Google account for convenience.
- **Priority**: P1 (Critical)
- **Rationale**: Simplifies onboarding and improves security.
- **One-sentence Test**: User clicks "Sign in with Google", authorizes, and is redirected back as a registered user.
- **Acceptance Scenario**:
    - **Given**: I am on the registration page.
    - **When**: I click the "Sign in with Google" button.
    - **Then**: I am redirected to Google, and after authorization, I return to LyricAI Studio as a logged-in user.

## [US3] Accessing Registration from Header
- **Description**: As a guest user, I want to find the registration page easily from any screen.
- **Priority**: P2 (High)
- **Rationale**: Ensures discoverability.
- **One-sentence Test**: Clicking the "Account" icon in the header opens the registration page.

# Requirements

## Functional Requirements
- **FR-001**: System MUST provide a standalone registration page.
- **FR-002**: Registration form MUST include fields: First Name, Last Name, Email.
- **FR-003**: System MUST validate that the email format is correct.
- **FR-004**: System MUST integrate Google OAuth2 for authentication.
- **FR-005**: System MUST prevent duplicate registrations with the same email.

## Technical Requirements
- **TR-001**: Backend MUST use FastAPI for auth endpoints.
- **TR-002**: System MUST store user records in a SQLite database.
- **TR-003**: System MUST use JWT (JSON Web Tokens) for session management.
- **TR-004**: System MUST store Google `sub` ID for OAuth users.

# Key Entities
- **User**: { id, first_name, last_name, email, google_id, created_at }

# Assumptions & Risks

## Assumptions
- Google Cloud Console is configured with OAuth 2.0 Client ID and Secret.
- Users have valid Google accounts for OAuth.
- Local storage or cookies can be used to store the JWT.

## Risks
- **OAuth Complexity**: Misconfiguration of redirect URIs can block the flow. (Likelihood: Med, Impact: High)
- **Security**: Improper JWT storage could lead to session hijacking. (Likelihood: Low, Impact: High)

# Implementation Signals
- **NEW-ENTITY**: `User` table in the database.
- **NEW-API**: `/register`, `/auth/google`, `/auth/google/callback` endpoints.
- **NEW-UI**: Registration page and header icon.
- **NEW-CONFIG**: `.env` variables for Google Client ID and Secret.

# Success Criteria
- **SC-001**: A user can register manually and their record appears in the database. [US1]
- **SC-002**: A user can log in via Google and their record is created/updated. [US2]
- **SC-003**: The "Account" icon is visible in the header and navigates to the registration page. [US3]
- **SC-004**: Secure JWT tokens are issued upon successful registration/login. [TR-003]

## Compliance Check
*(Pending Policy Auditor)*
