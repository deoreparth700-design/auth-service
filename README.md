# Authentication Service — FastAPI + PostgreSQL

A production-oriented authentication REST API built with **Python, FastAPI, PostgreSQL (Neon), JWT, bcrypt, and refresh-token rotation**.

This project implements a complete authentication lifecycle including user registration, secure password hashing, login, JWT access tokens, protected routes, refresh tokens, refresh-token rotation and revocation, logout, and login rate limiting.

---

## 🚀 Features

* User registration
* Email validation
* Secure password hashing with bcrypt
* User login
* JWT access tokens
* Protected authentication routes
* JWT authentication middleware
* Refresh tokens
* Refresh-token hashing before database storage
* Refresh-token expiration
* Refresh-token rotation
* Refresh-token revocation
* Logout
* Login rate limiting
* PostgreSQL database
* Neon PostgreSQL support
* Environment-variable based configuration
* Async database operations with `asyncpg`
* FastAPI Swagger/OpenAPI documentation

---

## 🛠️ Tech Stack

| Technology    | Purpose                         |
| ------------- | ------------------------------- |
| Python        | Backend language                |
| FastAPI       | REST API framework              |
| Uvicorn       | ASGI server                     |
| PostgreSQL    | Database                        |
| Neon          | Hosted PostgreSQL               |
| asyncpg       | Async PostgreSQL driver         |
| PyJWT         | JWT creation and verification   |
| bcrypt        | Password hashing                |
| Pydantic      | Request validation              |
| python-dotenv | Environment variable management |

---

## 📁 Project Structure

```text
auth-service-py/
│
├── app/
│   ├── controllers/
│   │   └── auth_controller.py
│   │
│   ├── db/
│   │   ├── pool.py
│   │   └── schema.sql
│   │
│   ├── models/
│   │   ├── user_model.py
│   │   └── refresh_token_model.py
│   │
│   ├── routes/
│   │   └── auth_routes.py
│   │
│   ├── utils/
│   │   ├── auth_middleware.py
│   │   ├── jwt_utils.py
│   │   ├── password_utils.py
│   │   ├── refresh_token_utils.py
│   │   └── rate_limiter.py
│   │
│   └── app.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── server.py
```

---

# 🔐 Authentication Architecture

The service uses short-lived JWT access tokens together with long-lived refresh tokens.

```text
                         ┌─────────────────┐
                         │     Client      │
                         └────────┬────────┘
                                  │
                                  ▼
                         POST /api/auth/login
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
              Verify bcrypt              Generate tokens
                password                       │
                    │                  ┌────────┴────────┐
                    │                  │                 │
                    ▼                  ▼                 ▼
                  User            Access Token      Refresh Token
                                     15 min            7 days
                                                          │
                                                          ▼
                                                    SHA-256 hash
                                                          │
                                                          ▼
                                                     PostgreSQL
```

---

# 🔑 Access Tokens

Access tokens are JWTs signed using `HS256`.

They contain the user's ID and expiration information.

Example payload:

```json
{
  "userId": 123,
  "iat": 1750000000,
  "exp": 1750000900
}
```

Access tokens expire after approximately **15 minutes**.

Clients send the access token using:

```text
Authorization: Bearer <access_token>
```

---

# 🔄 Refresh Tokens

Refresh tokens are randomly generated using Python's `secrets` module.

The raw refresh token is returned to the client, but **only its SHA-256 hash is stored in PostgreSQL**.

```text
Raw Refresh Token
        │
        ▼
    SHA-256
        │
        ▼
 PostgreSQL
```

Refresh tokens expire after **7 days**.

---

# 🔁 Refresh Token Rotation

Every successful refresh invalidates the previous refresh token.

```text
Refresh Token A
      │
      ▼
POST /api/auth/refresh
      │
      ├── Token A revoked
      │
      ├── New Access Token
      │
      └── New Refresh Token B
```

Trying to reuse Token A results in:

```text
401 Unauthorized
```

This helps protect against refresh-token replay.

---

# 🚪 Logout

Logout revokes the supplied refresh token.

```text
POST /api/auth/logout
        │
        ▼
Find refresh token
        │
        ▼
Set revoked_at
        │
        ▼
Token can no longer refresh
```

The current access token remains valid until its normal expiration. This is expected with short-lived stateless JWT access tokens.

---

# 🛡️ Login Rate Limiting

The login endpoint includes an in-memory rate limiter.

Current configuration:

```text
Maximum failed attempts: 5
Time window: 60 seconds
```

After the limit is reached:

```text
HTTP 429 Too Many Requests
```

Successful login clears the failed-attempt counter.

> Note: The current implementation stores rate-limit state in application memory. For a multi-instance production deployment, Redis or another shared store should be used.

---

# 🗄️ Database Schema

The service uses two primary tables.

## Users

```text
users
├── id
├── name
├── email
├── password_hash
├── created_at
└── updated_at
```

## Refresh Tokens

```text
refresh_tokens
├── id
├── user_id
├── token_hash
├── expires_at
├── created_at
└── revoked_at
```

The relationship is:

```text
users
  │
  │ 1
  │
  │
  │ N
  ▼
refresh_tokens
```

Deleting a user also deletes their refresh tokens using:

```sql
ON DELETE CASCADE
```

---

# 📡 API Endpoints

Base URL:

```text
/api/auth
```

| Method | Endpoint   | Authentication | Description          |
| ------ | ---------- | -------------- | -------------------- |
| POST   | `/signup`  | No             | Register a new user  |
| POST   | `/login`   | No             | Authenticate user    |
| GET    | `/me`      | Bearer Token   | Get current user     |
| POST   | `/refresh` | No             | Refresh access token |
| POST   | `/logout`  | No             | Revoke refresh token |

---

# 📝 Signup

### Request

```http
POST /api/auth/signup
Content-Type: application/json
```

```json
{
  "name": "Parth",
  "email": "parth@example.com",
  "password": "securepassword123"
}
```

### Response

```json
{
  "message": "User created successfully",
  "user": {
    "id": 1,
    "name": "Parth",
    "email": "parth@example.com",
    "created_at": "2026-08-28T12:00:00"
  }
}
```

---

# 🔑 Login

### Request

```http
POST /api/auth/login
Content-Type: application/json
```

```json
{
  "email": "parth@example.com",
  "password": "securepassword123"
}
```

### Response

```json
{
  "message": "Login successful",
  "accessToken": "<access_token>",
  "refreshToken": "<refresh_token>"
}
```

---

# 👤 Get Current User

### Request

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Response

```json
{
  "user": {
    "id": 1,
    "name": "Parth",
    "email": "parth@example.com",
    "created_at": "2026-08-28T12:00:00"
  }
}
```

---

# 🔄 Refresh Token

### Request

```http
POST /api/auth/refresh
Content-Type: application/json
```

```json
{
  "refreshToken": "<refresh_token>"
}
```

### Response

```json
{
  "message": "Token refreshed successfully",
  "accessToken": "<new_access_token>",
  "refreshToken": "<new_refresh_token>"
}
```

The previous refresh token is revoked.

---

# 🚪 Logout

### Request

```http
POST /api/auth/logout
Content-Type: application/json
```

```json
{
  "refreshToken": "<refresh_token>"
}
```

### Response

```json
{
  "message": "Logout successful"
}
```

---

# ⚙️ Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=your_neon_postgresql_connection_string
JWT_ACCESS_SECRET=your_strong_jwt_secret
PORT=3000
```

Never commit `.env` to Git.

Use `.env.example` for documenting required variables.

---

# 💻 Local Setup

## 1. Clone the repository

```bash
git clone https://github.com/deoreparth700-design/auth-service.git
cd auth-service
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create:

```text
.env
```

Add:

```env
DATABASE_URL=your_neon_database_url
JWT_ACCESS_SECRET=your_jwt_secret
PORT=3000
```

---

## 5. Initialize the database

Execute the SQL contained in:

```text
app/db/schema.sql
```

against your PostgreSQL/Neon database.

---

## 6. Start the server

```bash
python server.py
```

The API will be available at:

```text
http://localhost:3000
```

---

# 📚 API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://localhost:3000/docs
```

Alternative ReDoc documentation:

```text
http://localhost:3000/redoc
```

---

# 🧪 Authentication Flow

A typical client session works like this:

```text
1. Signup
       ↓
2. Login
       ↓
3. Receive Access + Refresh Tokens
       ↓
4. Use Access Token for protected requests
       ↓
5. Access Token expires
       ↓
6. Send Refresh Token
       ↓
7. Old Refresh Token revoked
       ↓
8. Receive new Access + Refresh Tokens
       ↓
9. Continue using API
       ↓
10. Logout
       ↓
11. Refresh Token revoked
```

---

# 🔒 Security Considerations

Implemented:

* bcrypt password hashing
* JWT signature verification
* short-lived access tokens
* hashed refresh tokens
* refresh-token expiration
* refresh-token rotation
* refresh-token revocation
* protected routes
* login rate limiting
* environment-based secrets
* PostgreSQL SSL connection

Future production improvements:

* Redis-based distributed rate limiting
* transactional refresh-token rotation
* secure HttpOnly cookies for browser clients
* CSRF protection when using cookies
* email verification
* password reset
* account lockout/security monitoring
* structured logging
* automated tests
* CI/CD
* stronger password policy
* refresh-token reuse detection
* centralized secret management

---

# 📌 Project Status

```text
FastAPI API                 ✅
PostgreSQL / Neon           ✅
User registration           ✅
bcrypt password hashing     ✅
Login                       ✅
JWT access tokens           ✅
Protected routes            ✅
JWT middleware              ✅
Refresh tokens              ✅
Token rotation              ✅
Token revocation            ✅
Logout                      ✅
Login rate limiting         ✅
Production configuration    ✅
Documentation               ✅
Deployment                  ⏳
```

---

# 👨‍💻 Author

**Parth Deore**

Computer Science & Engineering

GitHub:

https://github.com/deoreparth700-design

---

## 📄 License

This project is intended for learning, portfolio development, and backend engineering practice.
