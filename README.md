# SoftDesk API Documentation
Register:
post : http://127.0.0.1:8000/api/v1/register/ 

LogIn: 
post: http://127.0.0.1:8000/api/v1/token/

Refresh token:
post: http://127.0.0.1:8000/api/v1/token/refresh/

Create new project:
post : http://127.0.0.1:8000/api/v1/projects/

View all projects:
get: http://127.0.0.1:8000/api/v1/projects/

Check issues of the specific project
get : http://127.0.0.1:8000/api/v1/projects/<project_id>/issues/

## Create New Issue

**Endpoint:**

POST http://127.0.0.1:8000/api/v1/projects/<project_id>/issues/

**Description:**

This endpoint allows contributors to create a new issue for a specific project. The issue can be named, described, and optionally assigned to another contributor.

**Request Headers:**

- `Authorization: JWT <your_token>` 
- `Content-Type: application/json`

**Request Body:**
json
{
"name": "Issue Title",
"description": "Detailed description of the issue.",
"contributor": <contributor_id> // Optional: ID of the contributor to assign the issue to
}

**Response:**

201 Created: Issue created successfully.
400 Bad Request: Invalid request data.
401 Unauthorized: Invalid token.
403 Forbidden: User does not have permission to create an issue.
404 Not Found: Project or contributor not found.

bash
curl -X POST http://127.0.0.1:8000/api/v1/projects/1/issues/ \
-H "Authorization: Bearer your_token" \
-H "Content-Type: application/json" \
-d '{
"name": "New Feature",
"description": "Implement a new feature for the project.",
"contributor": 2
}'

**Notes:**

- Ensure that the `project_id` in the URL corresponds to an existing project.
- The `assignee` field is optional but must be a valid contributor of the project if provided.