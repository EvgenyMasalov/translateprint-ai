# API Contracts: User Registration & Google OAuth2

## POST /register
Manual user registration endpoint.

### Request
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string"
}
```

### Response (201 Created)
```json
{
  "status": "success",
  "message": "User registered successfully",
  "access_token": "jwt_token_here"
}
```

## GET /auth/google
Initiates Google OAuth2 flow by redirecting the user to Google.

### Response (302 Redirect)
Redirects to `https://accounts.google.com/o/oauth2/v2/auth?...`

## GET /auth/google/callback
Callback endpoint for Google OAuth2.

### Parameters
- `code`: Authorization code from Google.
- `state`: State parameter for CSRF protection.

### Response (302 Redirect)
Redirects to `/` (main page) with `token` in cookies or local storage.

## GET /me
Retrieve current user info (requires JWT).

### Response (200 OK)
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "avatar_url": "string"
}
```
