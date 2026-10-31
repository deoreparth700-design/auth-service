# Auth Service 🔐

[![Tests](https://github.com/deoreparth700-design/auth-service/actions/workflows/tests.yml/badge.svg)](https://github.com/deoreparth700-design/auth-service/actions/workflows/tests.yml)

A production-oriented authentication service built with **FastAPI, PostgreSQL, JWT, and Python**.

This project implements a complete authentication flow including user registration, secure password hashing, JWT access tokens, refresh tokens, protected routes, rate limiting, and a minimal web interface.

## 🚀 Live Demo

**Auth Service:**
https://auth-service-17bm.onrender.com

## ✨ Features

* User registration and login
* Secure password hashing with `bcrypt`
* JWT-based authentication
* Short-lived access tokens (15 minutes)
* Refresh token support (7 days) with rotation: every refresh revokes the old token and issues a new one
* Refresh tokens are stored in PostgreSQL as SHA-256 hashes, never in plaintext
* Logout that revokes the refresh token
* Protected `/me` endpoint
* Login rate limiting (5 failed attempts per minute per IP)
* Token validation and expiration handling
* PostgreSQL connection pooling with `asyncpg`
* Environment-based configuration
* Minimal login, signup, and dashboard interface
* Production deployment on Render

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn
* PostgreSQL
* asyncpg
* PyJWT
* bcrypt
* Pydantic

### Frontend

* HTML
* CSS
* Vanilla JavaScript

### Deployment

* Render
* PostgreSQL / Neon

## 📁 Project Structure

```text
auth-service/
│
├── app/
│   ├── app.py                  # FastAPI app, CORS, frontend pages, route mounting
│   ├── controllers/
│   │   └── auth_controller.py
│   │
│   ├── db/
│   │   ├── pool.py
│   │   ├── migrate.py          # creates the tables from schema.sql
│   │   └── schema.sql
│   │
│   ├── middleware/
│   │   └── auth.py
│   │
│   ├── models/
│   │   ├── user_model.py
│   │   └── refresh_token_model.py
│   │
│   ├── routes/
│   │   └── auth_routes.py
│   │
│   └── utils/
│       ├── auth_middleware.py
│       ├── jwt_utils.py
│       ├── password_utils.py
│       ├── rate_limiter.py
│       └── refresh_token_utils.py
│
├── frontend/
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
│
├── server.py                   # entrypoint: starts Uvicorn and the DB pool
├── requirements.txt
├── runtime.txt
├── .env.example
└── .gitignore
```

## 🔑 Authentication Flow

### 1. Registration

The user submits:

```http
POST /api/auth/signup
```

The service:

1. Validates the input (name, a valid-looking email, and a password of at least 8 characters).
2. Checks whether the email already exists (409 if it does).
3. Hashes the password using bcrypt.
4. Creates the user in PostgreSQL.
5. Returns the new user. It does not log the user in; call `/login` next.

### 2. Login

The user submits:

```http
POST /api/auth/login
```

The service:

1. Checks the rate limit for the client IP (more than 5 failed attempts in the last 60 seconds returns 429).
2. Finds the user by email.
3. Verifies the password. A wrong email or password counts as a failed attempt; a successful login clears the count.
4. Generates an access token (valid for 15 minutes).
5. Generates a refresh token (valid for 7 days).
6. Stores a SHA-256 hash of the refresh token in PostgreSQL.
7. Returns both tokens.

### 3. Protected Requests

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

The authentication middleware:

1. Extracts the JWT.
2. Verifies its signature.
3. Checks expiration.
4. Extracts the user ID.
5. Retrieves the user.
6. Allows the request to continue.

### 4. Refresh Token

When the access token expires, the client can request a new access token using:

```http
POST /api/auth/refresh
```

Send the refresh token in the JSON body as `{"refreshToken": "..."}`. The service checks that it exists, is not revoked and has not expired. It then revokes that token and returns a new access token **and** a new refresh token (rotation), so the old refresh token cannot be used again.

### 5. Logout

```http
POST /api/auth/logout
```

Send `{"refreshToken": "..."}`. The refresh token is revoked so it can no longer be used. Access tokens already issued stay valid until they expire (up to 15 minutes).

## 📡 API Endpoints

| Method | Endpoint            | Description                                  | Authentication                  |
| ------ | ------------------- | -------------------------------------------- | ------------------------------- |
| `POST` | `/api/auth/signup`  | Create a new account                         | No                              |
| `POST` | `/api/auth/login`   | Authenticate user, returns both tokens       | No                              |
| `POST` | `/api/auth/refresh` | Exchange a refresh token for new tokens      | Refresh token (in request body) |
| `POST` | `/api/auth/logout`  | Revoke a refresh token                       | Refresh token (in request body) |
| `GET`  | `/api/auth/me`      | Get authenticated user                       | Bearer token                    |

## 🧪 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/deoreparth700-design/auth-service.git
cd auth-service
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
PORT=3000
DATABASE_URL=your_postgresql_connection_string
JWT_ACCESS_SECRET=your_secret_key
```

Never commit `.env` to GitHub.

`DATABASE_URL` must point to a PostgreSQL server that accepts SSL connections (a free [Neon](https://neon.tech) database works). The connection pool always requires SSL, so a plain local PostgreSQL without SSL will fail to connect.

If you use the Blog Platform API or CartAPI with this service, they must verify tokens with the exact same secret: use the same value as `JWT_ACCESS_SECRET` in the Blog Platform API, and as `JWT_SECRET` in CartAPI.

### 5. Create the database tables

Run this once (it is safe to repeat, because the schema uses `CREATE TABLE IF NOT EXISTS`):

```bash
python -m app.db.migrate
```

### 6. Start the server

```bash
python server.py
```

The service will be available at:

```text
http://localhost:3000
```

## 🌐 Frontend

The project includes a minimal interface for testing the authentication system.

### Login

```text
/login.html
```

### Signup

```text
/signup.html
```

### Dashboard

```text
/dashboard.html
```

The frontend communicates with the FastAPI backend using the same-origin API endpoints:

```text
/api/auth/signup
/api/auth/login
/api/auth/refresh
/api/auth/logout
/api/auth/me
```

### Cross-origin access (CORS)

Browsers may only call this API from the origin listed in `app/app.py`, which is currently the deployed Blog Platform URL (`https://blog-platform-api-db7a.onrender.com`). Requests from other origins, including a Blog Platform frontend running on `localhost`, are blocked by the browser. To use another frontend origin, add it to `allow_origins` in `app/app.py`.

## 🔒 Security

The project includes several authentication security mechanisms:

* Passwords are never stored in plaintext.
* Passwords are hashed using bcrypt.
* Access tokens are signed using a server-side secret.
* Access tokens expire.
* Refresh tokens are persisted server-side.
* Protected endpoints require authentication.
* Invalid or expired tokens are rejected.
* Login attempts are rate limited (kept in memory, so the counts reset when the server restarts and are not shared between instances).
* Refresh tokens are stored only as SHA-256 hashes and rotate on every use.
* Secrets are stored through environment variables.
* `.env` is excluded from Git.

> **Production note:** For a larger production system, additional protections such as secure HTTP-only cookies, CSRF protection where applicable, distributed rate limiting, token revocation strategies, structured logging, monitoring, and secret management should be added.

## 🗄️ Database

The service uses **PostgreSQL** for persistent data.

The database stores user information and refresh-token data.

A shared `asyncpg` connection pool is used to efficiently manage database connections.

## ☁️ Deployment

The service is deployed using **Render**.

Production configuration is supplied through environment variables rather than committing secrets to the repository.

Python runtime is pinned to ensure consistent dependency installation.

## 🧪 Running tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Set the `TEST_DATABASE_URL` environment variable pointing to a test PostgreSQL database (the database name must contain `test` and must not equal `DATABASE_URL`):

```bash
# Example (Linux / macOS)
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/auth_test"

# Example (Windows PowerShell)
$env:TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/auth_test"
```

Run tests with `pytest`:

```bash
pytest -q
```

## 📚 What I Built

This project was built to understand authentication systems beyond basic CRUD APIs.

Key concepts implemented:

* REST API design
* Authentication vs. authorization
* Password hashing
* JWT authentication
* Access and refresh tokens
* Middleware
* Protected routes
* PostgreSQL connection pooling
* Rate limiting
* Environment configuration
* Frontend-to-backend integration
* Production deployment

## 👨‍💻 Author

**Parth Deore**

Computer Science & Engineering

GitHub:
https://github.com/deoreparth700-design

## 📄 License

This project is available for educational and portfolio purposes.
