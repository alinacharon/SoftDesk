 # SoftDesk API Documentation

## Register

****Endpoint:****

POST http://127.0.0.1:8000/api/v1/register/

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password",
    "age": 20,
    "can_be_contacted": true,
    "can_data_be_shared": false,
}
## LogIn
**Endpoint:**

POST http://127.0.0.1:8000/api/v1/token/

**Request Body:**

{
  "username": "your_username",
  "password": "your_password"
}
## Refresh Token
**Endpoint:**

POST http://127.0.0.1:8000/api/v1/token/refresh/

**Request Body:**


{
  "refresh": "your_refresh_token"
}
## Create New Project
**Endpoint:**

POST http://127.0.0.1:8000/api/v1/projects/

**Request Body:**

{
  "name": "Project Name",
  "description": "Project Description",
  "contributors": [1, 2, 3] // Optional: List of contributor IDs
}
## View All Projects
**Endpoint:**

GET http://127.0.0.1:8000/api/v1/projects/

## Check Issues of the Specific Project
**Endpoint:**

GET http://127.0.0.1:8000/api/v1/projects/<project_id>/issues/

## Create New Issue
**Endpoint:**

POST http://127.0.0.1:8000/api/v1/projects/<project_id>/issues/

Description:

This endpoint allows contributors to create a new issue for a specific project. The issue can be named, described, and optionally assigned to another contributor.

Request Headers:

Authorization: JWT <your_token>
Content-Type: application/json
**Request Body:**


{
  "name": "Issue Title",
  "description": "Detailed description of the issue.",
  "contributor": 1 // Optional: ID of the contributor to assign the issue to
}
Response:

201 Created: Issue created successfully.
400 Bad Request: Invalid request data.
401 Unauthorized: Invalid token.
403 Forbidden: User does not have permission to create an issue.
404 Not Found: Project or contributor not found.

## Update an Issue
**Endpoint:**

PATCH http://127.0.0.1:8000/api/v1/projects/<project_id>/issues/<issue_id>/

Description:

This endpoint allows contributors to update an existing issue.

Request Headers:

Authorization: JWT <your_token>
Content-Type: application/json
**Request Body:**


{
  "name": "Updated Issue Title",
  "description": "Updated description of the issue.",
  "contributor": 3 // Optional: ID of the new contributor to assign the issue to
}
Response:

200 OK: Issue updated successfully.
400 Bad Request: Invalid request data.
401 Unauthorized: Invalid token.
403 Forbidden: User does not have permission to update the issue.
404 Not Found: Project, issue, or contributor not found.