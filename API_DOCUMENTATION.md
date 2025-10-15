# API Documentation

This guide details the available API endpoints for the Domain Monitoring System.

**Base URL:** All endpoints are prefixed with `/api`.

**Authentication:** Most endpoints require an active user session. The API uses a secure, server-side session cookie that is automatically handled by the browser after a successful login via the `/api/login` endpoint. If a session is not active or is invalid, the API will respond with a `401 Unauthorized` status.

---

## Authentication & Session

### POST /api/register
Registers a new user account.

**Request Body:** `application/json`
```json
{
  "username": "new_user",
  "password": "a_strong_password"
}
Success Response (201 Created):
code
JSON
{
  "success": true,
  "message": "Registration successful"
}
Error Responses:
400 Bad Request: If username or password are missing.
code
JSON
{
  "success": false,
  "message": "Username and password are required."
}
409 Conflict: If the username already exists.
code
JSON
{
  "success": false,
  "message": "username already exists"
}
POST /api/login
Logs in a user and creates a session cookie.
Request Body: application/json
code
JSON
{
  "username": "existing_user",
  "password": "the_correct_password"
}
Success Response (200 OK):
code
JSON
{
  "success": true,
  "message": "Login successful"
}
Error Response (401 Unauthorized): If credentials are invalid.
code
JSON
{
  "success": false,
  "message": "invalid credentials"
}
POST /api/logout
Logs out the current user and clears their session.
Request Body: None.
Success Response (200 OK):
code
JSON
{
  "success": true,
  "message": "You have been logged out."
}
GET /api/session
Checks if a user is currently authenticated by verifying their session cookie. This is useful for a frontend to determine if it should display a login page or a dashboard.
Request Body: None.
Success Response (200 OK): If the user has a valid session.
code
JSON
{
  "loggedIn": true,
  "username": "current_user"
}
Error Response (401 Unauthorized): If the user does not have a valid session.
code
JSON
{
  "loggedIn": false
}
Domain Management
GET /api/domains
Retrieves the current user's full list of monitored domains and triggers a fresh status check on them.
Authentication: Required.
Request Body: None.
Success Response (200 OK):
Returns an array of domain objects. The array will be empty if the user has no domains.
Field Descriptions:
domain: The domain name that was checked.
status: A string indicating the liveness of the domain (e.g., "Live. Status code 200").
ssl_issuer: The common name of the SSL certificate's issuing authority.
ssl_expiration: The SSL certificate's expiration date in YYYY-MM-DD format. If an SSL check fails, this field will contain a specific error message (e.g., "DNS resolution failed", "SSL certificate invalid", etc.).
Example Response:
code
JSON
[
  {
    "domain": "example.com",
    "ssl_expiration": "2025-10-22",
    "ssl_issuer": "Let's Encrypt",
    "status": "Live. Status code 200"
  },
  {
    "domain": "another-site.org",
    "ssl_expiration": "N/A",
    "ssl_issuer": "N/A",
    "status": "Unavailable. Status code FAILED"
  }
]
Error Response (401 Unauthorized): If the user is not logged in.
POST /api/add_domain
Adds a single new domain to the user's monitoring list.
Authentication: Required.
Request Body: application/json
code
JSON
{
  "domain": "new-domain.com"
}
Success Response (201 Created):
code
JSON
{
  "success": true,
  "message": "Domain 'new-domain.com' was added successfully."
}
Error Responses:
400 Bad Request: If the domain format is invalid or the field is empty.
code
JSON
{
  "success": false,
  "message": "Invalid domain format. Please use a format like 'example.com'."
}
409 Conflict: If the domain is already in the user's list.
code
JSON
{
  "success": false,
  "message": "Domain 'new-domain.com' is already in your list."
}
401 Unauthorized: If the user is not logged in.
POST /api/remove_domain
Removes a domain from the user's monitoring list.
Authentication: Required.
Request Body: application/json
code
JSON
{
  "domain": "domain-to-remove.com"
}
Success Response (200 OK):
code
JSON
{
  "success": true,
  "message": "Domain 'domain-to-remove.com' was removed."
}
Error Responses:
404 Not Found: If the specified domain does not exist in the user's list.
code
JSON
{
  "success": false,
  "message": "Domain 'domain-to-remove.com' not found."
}
401 Unauthorized: If the user is not logged in.
POST /api/bulk_upload
Adds multiple domains to the user's list from an uploaded .txt file. Each domain should be on a new line.
Authentication: Required.
Request Body: multipart/form-data
The request must contain a file attached to a form field named file.
Success Response (200 OK):
code
JSON
{
  "success": true,
  "message": "Bulk upload complete. Added 5 new domains."
}
Error Responses:
400 Bad Request: If no file is provided, the file is not a .txt file, or the file is empty.
code
JSON
{
  "success": false,
  "message": "Please upload a valid .txt file."
}
401 Unauthorized: If the user is not logged in.