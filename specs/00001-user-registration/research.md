# Research: User Registration and Google OAuth2 Integration

## Domain Best Practices
- **Registration Workflow**: Implement a multi-step or single-page form with validation. Ensure clear feedback for existing emails.
- **Google OAuth2**: Use Authorization Code Flow. Key security measures: `state` parameter for CSRF protection, secure HTTP-only cookies for JWT/Session, and validation of the `id_token`.
- **User Identity**: Identify users by a unique, immutable ID (Google `sub`) rather than just email, which can change.

## Technical Patterns (FastAPI)
- **Library Choice**: `FastAPI Users` is recommended for high-level abstraction. For more control, use `Authlib` or `httpx` for manual token exchange.
- **JWT Management**: Use `PyJWT`. Access tokens should be short-lived (15-30m), refresh tokens stored securely.
- **Database**: SQLite or MongoDB. Unique index on `email` is mandatory.

## UX/UI Best Practices
- **Visibility**: Place registration/login icon in the header (right side). Use a "Person" or "Account" icon.
- **Feedback**: Immediate validation for required fields (Username, Last Name, Email).
- **Google Branding**: Follow Google Identity branding guidelines (standard "Sign in with Google" button).

## Risks & Edge Cases
- **Duplicate Emails**: Handling cases where a user registered via form and then tries Google Auth with the same email.
- **Token Expiry**: Seamless re-authentication or refresh token usage.
- **Privacy**: Only request necessary scopes from Google (`openid`, `email`, `profile`).
