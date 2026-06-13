# TEOS API Full Reference

## Authentication

### POST /auth/login
**Body:** `{ "username": "admin", "password": "admin" }`  
**Response:** `{ "access_token": "...", "token_type": "bearer" }`

## Admin Users

### GET /admin/users?search=term&page=1
**Headers:** `Authorization: Bearer <token>`  
**Response:** `[ { "id": 1, "telegram_id": 123, "full_name": "John", "role": "user", "is_blocked": false }, ... ]`

### PUT /admin/users/{id}
**Body:** `{ "role": "admin_music", "is_blocked": true }`

## Admin Music

### GET /admin/music/tracks?search=love&page=1
**Response:** `[ { "id": 1, "title": "...", "artist": "...", "plays": 42, "is_active": true } ]`

### POST /admin/music/tracks
**Body:** `{ "title": "New", "artist": "Artist", "genre": "pop", "file_id": "..." }`

### PUT /admin/music/tracks/{id}
**Body:** `{ "title": "Updated", "is_active": false }`

### DELETE /admin/music/tracks/{id} (soft delete)

## Admin Transactions

### GET /admin/transactions/pending
**Response:** `[ { "id": 1, "type": "deposit", "amount": 50000, "status": "pending", "description": "شارژ" } ]`

### POST /admin/transactions/{id}/approve
### POST /admin/transactions/{id}/reject
**Body:** `{ "reason": "مبلغ اشتباه" }`

## Owner Menus

### GET /owner/menus/tree
**Response:** hierarchical JSON

### POST /owner/menus/node
**Body:** `{ "key": "new_item", "label": "آیتم جدید", "parent_key": "main", "callback_data": "..." }`

## Entity Builder

### POST /entity-builder/definitions
**Body:** `{ "name": "Student", "fields_schema": [{"name":"age","type":"integer","required":true}] }`

### POST /entity-builder/records/Student
**Body:** `{ "data": { "age": 22 } }`

## Workflow Designer

### POST /workflow-designer/
**Body:** `{ "name": "Approval", "graph": {...} }`

### PUT /workflow-designer/{id}
**Body:** `{ "graph": {...} }`

## Plugins

### POST /plugins/upload
**Form:** file (Python plugin file)

## GraphQL
Endpoint: `/graphql`  
Playground: `/graphql`
