# API Contracts: Song Persistence

## GET /songs
List all songs for the authenticated user.

### Response (200 OK)
```json
[
  {
    "id": "uuid",
    "title": "Song Title",
    "updated_at": "timestamp"
  }
]
```

## POST /songs
Save a new song or update an existing one.

### Request
```json
{
  "id": "uuid (optional)",
  "title": "string",
  "lyrics": "string",
  "structure": "string (optional)",
  "metaphors": "string (optional)",
  "mood": "string (optional)",
  "translation": "string (optional)",
  "target_language": "string (optional)"
}
```

### Response (201 Created / 200 OK)
```json
{
  "id": "uuid",
  "status": "saved"
}
```

## GET /songs/{id}
Retrieve full details of a specific song.

### Response (200 OK)
```json
{
  "id": "uuid",
  "title": "string",
  "lyrics": "string",
  "structure": "string",
  "metaphors": "string",
  "mood": "string",
  "translation": "string",
  "target_language": "string"
}
```

## DELETE /songs/{id}
Delete a song.

### Response (204 No Content)
