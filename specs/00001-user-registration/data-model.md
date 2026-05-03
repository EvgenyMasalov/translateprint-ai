# Data Model: User Registration

## Entities

### User
Represents a registered user in the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| first_name | String | Not Null | User's first name |
| last_name | String | Not Null | User's last name |
| email | String | Unique, Index | User's email address |
| google_id | String | Unique, Nullable | Google sub ID for OAuth |
| avatar_url | String | Nullable | URL to user's avatar |
| created_at | DateTime | Default: Now | Account creation timestamp |

## State Transitions
1. **Unregistered**: Guest user.
2. **Pending OAuth**: User redirected to Google.
3. **Registered (Active)**: Record created in SQLite database.

## Validation Rules
- Email must follow standard regex format.
- Names must be non-empty strings.
- Either `google_id` or a future password (not in scope) must exist for login.
