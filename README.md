# SoftDesk API Documentation

## Authentication Endpoints

### Register

**Endpoint:** `POST /api/v1/register/`

**Description:** Register a new user account.

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password",
    "age": 20,
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```

**Notes:**
- Users must be at least 15 years old to consent to data sharing
- Already authenticated users cannot register again

### Login

**Endpoint:** `POST /api/v1/token/`

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

### Refresh Token

**Endpoint:** `POST /api/v1/token/refresh/`

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

### Verify Token

**Endpoint:** `POST /api/v1/token/verify/`

**Request Body:**
```json
{
    "token": "your_access_token"
}
```

## User Profile

### View/Update Profile

**Endpoint:** `GET/PUT /api/v1/profile/`

**Description:** Retrieve or update the authenticated user's profile.

**Authentication:** Required

**Request Body (for PUT):**
```json
{
    "username": "updated_username",
    // Other user fields you want to update
}
```

## Projects

### Create New Project

**Endpoint:** `POST /api/v1/projects/`

**Authentication:** Required

**Request Body:**
```json
{
    "name": "Project Name",
    "description": "Project Description",
    "type": "Project type", // Options: 
    "contributors": [1, 2, 3]  // Optional: List of contributor IDs
}
```

### View All Projects

**Endpoint:** `GET /api/v1/projects/`

**Authentication:** Required

**Description:** Returns all projects where the authenticated user is a contributor.

### Manage Project Contributors

#### Add Contributor

**Endpoint:** `POST /api/v1/projects/{project_id}/add_contributor/`

**Authentication:** Required

**Permission:** Project owner only

**Request Body:**
```json
{
    "user_id": 1
}
```

#### Remove Contributor

**Endpoint:** `DELETE /api/v1/projects/{project_id}/remove_contributor/`

**Authentication:** Required

**Permission:** Project owner only

**Request Body:**
```json
{
    "user_id": 1
}
```

## Issues

### Create New Issue

**Endpoint:** `POST /api/v1/issues/`

**Authentication:** Required

**Permission:** Project contributors only

**Request Body:**
```json
{
    "name": "Issue Title",
    "type": "BUG",  // Options: 'BUG', 'FEATURE', 'TASK'
    "level": "LOW",  // Options: 'LOW', 'MEDIUM', 'HIGH'
    "status": "To do", // Options:'To Do','In Progress','Finished'.By default = 'To do'.
    "assigned_users": [1],  // Optional: List of contributor IDs
    "project": 1  // Required: Project ID
}
```

### View Issues

**Endpoint:** `GET /api/v1/issues/`

**Authentication:** Required

**Description:** Returns all issues for projects where the user is a contributor.

## Comments

### Manage Comments

**Base Endpoint:** `/api/v1/comments/`

**Authentication:** Required

**Permissions:** 
- View: Project contributors
- Create/Update/Delete: Comment owner or project admin

## Contributors

### View Contributors

**Endpoint:** `GET /api/v1/contributors/`

**Authentication:** Required

**Permission:** Admin only

**Query Parameters:**
- `project_id`: Optional. Filter contributors by specific project

## General Notes

- All endpoints except registration and login require authentication
- Authentication is done using JWT tokens
- Include the token in the Authorization header: `Authorization: JWT <your_token>`
- All requests should include `Content-Type: application/json` header

## Error Responses

Common error status codes:
- 400 Bad Request: Invalid data provided
- 401 Unauthorized: Authentication required or invalid
- 403 Forbidden: User doesn't have required permissions
- 404 Not Found: Requested resource doesn't exist