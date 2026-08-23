# Authentication Service

A secure REST API for user authentication and session management built with **Node.js, Express.js, PostgreSQL, and JWT**.

The project demonstrates practical backend authentication concepts including password hashing, short-lived access tokens, refresh-token rotation/revocation, protected routes, rate limiting, and secure cookie handling.

## Features

* User registration
* User login
* Secure password hashing with bcrypt
* JWT access-token authentication
* Short-lived access tokens
* Refresh-token based sessions
* Protected API routes
* Logout and refresh-token revocation
* HttpOnly cookies for refresh tokens
* Login rate limiting
* PostgreSQL database
* Parameterized SQL queries
* Environment-based configuration

## Tech Stack

| Technology    | Purpose            |
| ------------- | ------------------ |
| Node.js       | Backend runtime    |
| Express.js    | REST API framework |
| PostgreSQL    | Database           |
| Neon          | Hosted PostgreSQL  |
| JWT           | Authentication     |
| bcrypt        | Password hashing   |
| cookie-parser | Cookie handling    |
| Render        | Deployment         |
| Git & GitHub  | Version control    |

## Authentication Flow

```text
Client
  │
  ├── Register ──► API ──► Hash Password ──► PostgreSQL
  │
  ├── Login ─────► API ──► Verify Password
  │                         │
  │                         ├── Access Token
  │                         └── Refresh Token
  │
  ├── Protected Request ──► JWT Verification ──► API
  │
  ├── Refresh ────────────► Validate Refresh Token
  │                         │
  │                         └── Issue New Access Token
  │
  └── Logout ──────────────► Revoke Refresh Token
```

## Project Structure

```text
auth-service/
│
├── src/
│   ├── controllers/
│   │   └── auth.controller.js
│   │
│   ├── db/
│   │   ├── migrate.js
│   │   ├── pool.js
│   │   └── schema.sql
│   │
│   ├── middleware/
│   │
│   ├── models/
│   │   └── user.model.js
│   │
│   ├── routes/
│   │   └── auth.routes.js
│   │
│   └── utils/
│       ├── jwt.js
│       └── password.js
│
├── .env.example
├── .gitignore
├── package.json
├── package-lock.json
├── server.js
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/deoreparth700-design/auth-service.git
cd auth-service
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

Create a `.env` file based on `.env.example`.

```env
PORT=5000
DATABASE_URL=your_postgresql_connection_string
JWT_SECRET=your_jwt_secret
JWT_REFRESH_SECRET=your_refresh_token_secret
```

Never commit your `.env` file or production secrets to GitHub.

### 4. Run database migrations

```bash
npm run migrate
```

### 5. Start the server

For development:

```bash
npm run dev
```

Or start normally:

```bash
npm start
```

The API will be available at:

```text
http://localhost:5000
```

## Security

This project follows several important backend security practices:

* Passwords are never stored in plaintext.
* Passwords are hashed using bcrypt.
* JWT signatures are verified before accessing protected resources.
* Refresh tokens are stored using HttpOnly cookies.
* Authentication endpoints are rate-limited.
* Secrets are loaded through environment variables.
* SQL queries use parameterized statements.
* Authentication failures use generic error messages to avoid unnecessary information disclosure.

## API Overview

Typical authentication operations include:

| Method | Endpoint         | Description                    |
| ------ | ---------------- | ------------------------------ |
| `POST` | `/auth/register` | Register a new user            |
| `POST` | `/auth/login`    | Authenticate a user            |
| `POST` | `/auth/refresh`  | Generate a new access token    |
| `POST` | `/auth/logout`   | Revoke the refresh token       |
| `GET`  | Protected route  | Access authenticated resources |

> Check the route definitions in `src/routes/` for the exact endpoints implemented in the current version.

## Database

The application uses PostgreSQL with the following core entities:

* **Users** — stores user account information and hashed passwords.
* **Refresh Tokens** — stores session/refresh-token information associated with users.

A foreign-key relationship connects refresh tokens to their corresponding users.

## Deployment

The API is designed to be deployable using:

* **Render** for the backend
* **Neon** for hosted PostgreSQL

Production secrets should be configured through the deployment platform's environment variables rather than committed to the repository.

## What This Project Demonstrates

This project was built to gain practical experience with:

* REST API development
* Authentication and authorization
* JWT-based authentication
* Refresh-token sessions
* Password security
* PostgreSQL database design
* Backend security practices
* Environment configuration
* API deployment
* Git and GitHub workflows

## License

This project is intended for educational and portfolio purposes.
