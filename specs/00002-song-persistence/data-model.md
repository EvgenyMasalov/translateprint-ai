# Data Model: Song Persistence

## Entities

### Song
Represents a user's song project.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| user_id | UUID | FK -> User.id | Owner of the song |
| title | String | Not Null | Song name |
| lyrics | Text | Not Null | Original lyrics content |
| structure | Text | Nullable | Analyzed rhythm/meter |
| metaphors | Text | Nullable | Poetic devices |
| mood | Text | Nullable | Emotional analysis |
| translation | Text | Nullable | Literal translation |
| target_language| String | Nullable | Target language for translation |
| created_at | DateTime | Default: Now | Creation timestamp |
| updated_at | DateTime | Default: Now | Last modification timestamp |

## Relationships
- **User (1) --- (N) Song**: A user can have many songs; a song belongs to one user.

## state Transitions
1. **New**: Freshly created in the editor.
2. **Saved**: Persisted in SQLite.
3. **Modified**: Local changes pending save.
4. **Deleted**: Removed from DB.
