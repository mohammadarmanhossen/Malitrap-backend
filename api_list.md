<!-- # Mailtrap Backend API Documentation

All API endpoints are prefixed with `/api/`.

## Authentication

### Register
- **URL**: `/auth/register/`
- **Method**: `POST`
- **Auth Required**: No
- **Payload**:
  ```json
  {
    "username": "user",
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```

### Login
- **URL**: `/auth/login/`
- **Method**: `POST`
- **Auth Required**: No
- **Payload**:
  ```json
  {
    "username": "user",
    "password": "securepassword"
  }
  ```
- **Response**: JWT access and refresh tokens.

### Refresh Token
- **URL**: `/auth/refresh/`
- **Method**: `POST`
- **Auth Required**: No
- **Payload**:
  ```json
  {
    "refresh": "token"
  }
  ```

---

## Inboxes

### List Inboxes
- **URL**: `/inboxes/`
- **Method**: `GET`
- **Auth Required**: Yes

### Create Inbox
- **URL**: `/inboxes/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Payload**:
  ```json
  {
    "name": "My Inbox",
    "email_address": "inbox@example.com"
  }
  ```

### Get Inbox Details
- **URL**: `/inboxes/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes

### Delete Inbox
- **URL**: `/inboxes/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes

### Clear Inbox (Delete all emails)
- **URL**: `/inboxes/{id}/clear/`
- **Method**: `DELETE`
- **Auth Required**: Yes

---

## Emails

### List Emails
- **URL**: `/emails/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Params**: `?inbox={inbox_uuid}` (optional)

### Get Email Details
- **URL**: `/emails/{id}/`
- **Method**: `GET`
- **Auth Required**: Yes

### Delete Email
- **URL**: `/emails/{id}/`
- **Method**: `DELETE`
- **Auth Required**: Yes

---

## Testing

### Send Test Email
- **URL**: `/send-test/`
- **Method**: `POST`
- **Auth Required**: Yes
- **Payload**:
  ```json
  {
    "inbox_id": "uuid",
    "from_addr": "sender@test.com",
    "to_addr": "recipient@test.com",
    "subject": "Test",
    "body_text": "Hello world",
    "body_html": "<h1>Hello world</h1>"
  }
  ``` -->
