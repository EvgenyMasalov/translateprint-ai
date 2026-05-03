# API Contracts: User Profile & Settings

## GET /me
Retrieve current user info including statistics.

### Response (200 OK)
```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "avatar_url": "string",
  "stats": {
    "total_songs": 10
  }
}
```

## PUT /me
Update current user's personal information.

### Request
```json
{
  "first_name": "string",
  "last_name": "string"
}
```

### Response (200 OK)
```json
{
  "status": "success",
  "message": "Profile updated successfully"
}
```
