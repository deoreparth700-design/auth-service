# Auth Service 🔐

A production-oriented authentication service built with **FastAPI, PostgreSQL, JWT, and Python**.

This project implements a complete authentication flow including user registration, secure password hashing, JWT access tokens, refresh tokens, protected routes, rate limiting, and a minimal web interface.

## 🚀 Live Demo

**Auth Service:**
https://auth-service-17bm.onrender.com

## ✨ Features

* User registration and login
* Secure password hashing with `bcrypt`
* JWT-based authentication
* Short-lived access tokens
* Refresh token support
* Refresh token persistence in PostgreSQL
* Protected `/me` endpoint
* Login rate limiting
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
│   ├── controllers/
│   │   └── auth_controller.py
│   │
│   ├── db/
│   │   └── pool.py
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
│       ├── rate_limiter.py
│       └── refresh_token_utils.py
│
├── frontend/
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
│
├── app.py
├── server.py
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

1. Validates the input.
2. Checks whether the email already exists.
3. Hashes the password using bcrypt.
4. Creates the user in PostgreSQL.
5. Returns the registration result.

### 2. Login

The user submits:

```http
POST /api/auth/login
```

The service:

1. Finds the user by email.
2. Verifies the password.
3. Applies login rate limiting.
4. Generates an access token.
5. Generates a refresh token.
6. Stores the refresh token in PostgreSQL.

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

The refresh token is validated against the stored token before issuing a new access token.

## 📡 API Endpoints

| Method | Endpoint            | Description            | Authentication |
| ------ | ------------------- | ---------------------- | -------------- |
| `POST` | `/api/auth/signup`  | Create a new account   | No             |
| `POST` | `/api/auth/login`   | Authenticate user      | No             |
| `POST` | `/api/auth/refresh` | Refresh access token   | Refresh token  |
| `GET`  | `/api/auth/me`      | Get authenticated user | Bearer token   |

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

### 5. Start the server

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
/api/auth/me
```

## 🔒 Security

The project includes several authentication security mechanisms:

* Passwords are never stored in plaintext.
* Passwords are hashed using bcrypt.
* Access tokens are signed using a server-side secret.
* Access tokens expire.
* Refresh tokens are persisted server-side.
* Protected endpoints require authentication.
* Invalid or expired tokens are rejected.
* Login attempts are rate limited.
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

```
```
