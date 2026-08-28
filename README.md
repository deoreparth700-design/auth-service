\# Authentication Service — FastAPI + PostgreSQL



A production-oriented authentication REST API built with \*\*Python, FastAPI, PostgreSQL (Neon), JWT, bcrypt, and refresh-token rotation\*\*.



This project implements a complete authentication lifecycle including user registration, secure password hashing, login, JWT access tokens, protected routes, refresh tokens, refresh-token rotation and revocation, logout, and login rate limiting.



\---



\## 🚀 Features



\* User registration

\* Email validation

\* Secure password hashing with bcrypt

\* User login

\* JWT access tokens

\* Protected authentication routes

\* JWT authentication middleware

\* Refresh tokens

\* Refresh-token hashing before database storage

\* Refresh-token expiration

\* Refresh-token rotation

\* Refresh-token revocation

\* Logout

\* Login rate limiting

\* PostgreSQL database

\* Neon PostgreSQL support

\* Environment-variable based configuration

\* Async database operations with `asyncpg`

\* FastAPI Swagger/OpenAPI documentation



\---



\## 🛠️ Tech Stack



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



\---



\## 📁 Project Structure



```text

auth-service-py/

│

├── app/

│   ├── controllers/

│   │   └── auth\_controller.py

│   │

│   ├── db/

│   │   ├── pool.py

│   │   └── schema.sql

│   │

│   ├── models/

│   │   ├── user\_model.py

│   │   └── refresh\_token\_model.py

│   │

│   ├── routes/

│   │   └── auth\_routes.py

│   │

│   ├── utils/

│   │   ├── auth\_middleware.py

│   │   ├── jwt\_utils.py

│   │   ├── password\_utils.py

│   │   ├── refresh\_token\_utils.py

│   │   └── rate\_limiter.py

│   │

│   └── app.py

│

├── .env.example

├── .gitignore

├── requirements.txt

├── README.md

└── server.py

```



\---



\# 🔐 Authentication Architecture



The service uses short-lived JWT access tokens together with long-lived refresh tokens.



```text

&#x20;                        ┌─────────────────┐

&#x20;                        │     Client      │

&#x20;                        └────────┬────────┘

&#x20;                                 │

&#x20;                                 ▼

&#x20;                        POST /api/auth/login

&#x20;                                 │

&#x20;                   ┌─────────────┴─────────────┐

&#x20;                   │                           │

&#x20;                   ▼                           ▼

&#x20;             Verify bcrypt              Generate tokens

&#x20;               password                       │

&#x20;                   │                  ┌────────┴────────┐

&#x20;                   │                  │                 │

&#x20;                   ▼                  ▼                 ▼

&#x20;                 User            Access Token      Refresh Token

&#x20;                                    15 min            7 days

&#x20;                                                         │

&#x20;                                                         ▼

&#x20;                                                   SHA-256 hash

&#x20;                                                         │

&#x20;                                                         ▼

&#x20;                                                    PostgreSQL

```



\---



\# 🔑 Access Tokens



Access tokens are JWTs signed using `HS256`.



They contain the user's ID and expiration information.



Example payload:



```json

{

&#x20; "userId": 123,

&#x20; "iat": 1750000000,

&#x20; "exp": 1750000900

}

```



Access tokens expire after approximately \*\*15 minutes\*\*.



Clients send the access token using:



```text

Authorization: Bearer <access\_token>

```



\---



\# 🔄 Refresh Tokens



Refresh tokens are randomly generated using Python's `secrets` module.



The raw refresh token is returned to the client, but \*\*only its SHA-256 hash is stored in PostgreSQL\*\*.



```text

Raw Refresh Token

&#x20;       │

&#x20;       ▼

&#x20;   SHA-256

&#x20;       │

&#x20;       ▼

&#x20;PostgreSQL

```



Refresh tokens expire after \*\*7 days\*\*.



\---



\# 🔁 Refresh Token Rotation



Every successful refresh invalidates the previous refresh token.



```text

Refresh Token A

&#x20;     │

&#x20;     ▼

POST /api/auth/refresh

&#x20;     │

&#x20;     ├── Token A revoked

&#x20;     │

&#x20;     ├── New Access Token

&#x20;     │

&#x20;     └── New Refresh Token B

```



Trying to reuse Token A results in:



```text

401 Unauthorized

```



This helps protect against refresh-token replay.



\---



\# 🚪 Logout



Logout revokes the supplied refresh token.



```text

POST /api/auth/logout

&#x20;       │

&#x20;       ▼

Find refresh token

&#x20;       │

&#x20;       ▼

Set revoked\_at

&#x20;       │

&#x20;       ▼

Token can no longer refresh

```



The current access token remains valid until its normal expiration. This is expected with short-lived stateless JWT access tokens.



\---



\# 🛡️ Login Rate Limiting



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



\---



\# 🗄️ Database Schema



The service uses two primary tables.



\## Users



```text

users

├── id

├── name

├── email

├── password\_hash

├── created\_at

└── updated\_at

```



\## Refresh Tokens



```text

refresh\_tokens

├── id

├── user\_id

├── token\_hash

├── expires\_at

├── created\_at

└── revoked\_at

```



The relationship is:



```text

users

&#x20; │

&#x20; │ 1

&#x20; │

&#x20; │

&#x20; │ N

&#x20; ▼

refresh\_tokens

```



Deleting a user also deletes their refresh tokens using:



```sql

ON DELETE CASCADE

```



\---



\# 📡 API Endpoints



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



\---



\# 📝 Signup



\### Request



```http

POST /api/auth/signup

Content-Type: application/json

```



```json

{

&#x20; "name": "Parth",

&#x20; "email": "parth@example.com",

&#x20; "password": "securepassword123"

}

```



\### Response



```json

{

&#x20; "message": "User created successfully",

&#x20; "user": {

&#x20;   "id": 1,

&#x20;   "name": "Parth",

&#x20;   "email": "parth@example.com",

&#x20;   "created\_at": "2026-08-28T12:00:00"

&#x20; }

}

```



\---



\# 🔑 Login



\### Request



```http

POST /api/auth/login

Content-Type: application/json

```



```json

{

&#x20; "email": "parth@example.com",

&#x20; "password": "securepassword123"

}

```



\### Response



```json

{

&#x20; "message": "Login successful",

&#x20; "accessToken": "<access\_token>",

&#x20; "refreshToken": "<refresh\_token>"

}

```



\---



\# 👤 Get Current User



\### Request



```http

GET /api/auth/me

Authorization: Bearer <access\_token>

```



\### Response



```json

{

&#x20; "user": {

&#x20;   "id": 1,

&#x20;   "name": "Parth",

&#x20;   "email": "parth@example.com",

&#x20;   "created\_at": "2026-08-28T12:00:00"

&#x20; }

}

```



\---



\# 🔄 Refresh Token



\### Request



```http

POST /api/auth/refresh

Content-Type: application/json

```



```json

{

&#x20; "refreshToken": "<refresh\_token>"

}

```



\### Response



```json

{

&#x20; "message": "Token refreshed successfully",

&#x20; "accessToken": "<new\_access\_token>",

&#x20; "refreshToken": "<new\_refresh\_token>"

}

```



The previous refresh token is revoked.



\---



\# 🚪 Logout



\### Request



```http

POST /api/auth/logout

Content-Type: application/json

```



```json

{

&#x20; "refreshToken": "<refresh\_token>"

}

```



\### Response



```json

{

&#x20; "message": "Logout successful"

}

```



\---



\# ⚙️ Environment Variables



Create a `.env` file in the project root.



```env

DATABASE\_URL=your\_neon\_postgresql\_connection\_string

JWT\_ACCESS\_SECRET=your\_strong\_jwt\_secret

PORT=3000

```



Never commit `.env` to Git.



Use `.env.example` for documenting required variables.



\---



\# 💻 Local Setup



\## 1. Clone the repository



```bash

git clone https://github.com/deoreparth700-design/auth-service.git

cd auth-service

```



\## 2. Create a virtual environment



Windows:



```powershell

python -m venv .venv

```



Activate it:



```powershell

.venv\\Scripts\\activate

```



\---



\## 3. Install dependencies



```bash

pip install -r requirements.txt

```



\---



\## 4. Configure environment variables



Create:



```text

.env

```



Add:



```env

DATABASE\_URL=your\_neon\_database\_url

JWT\_ACCESS\_SECRET=your\_jwt\_secret

PORT=3000

```



\---



\## 5. Initialize the database



Execute the SQL contained in:



```text

app/db/schema.sql

```



against your PostgreSQL/Neon database.



\---



\## 6. Start the server



```bash

python server.py

```



The API will be available at:



```text

http://localhost:3000

```



\---



\# 📚 API Documentation



FastAPI automatically provides interactive Swagger documentation.



Open:



```text

http://localhost:3000/docs

```



Alternative ReDoc documentation:



```text

http://localhost:3000/redoc

```



\---



\# 🧪 Authentication Flow



A typical client session works like this:



```text

1\. Signup

&#x20;      ↓

2\. Login

&#x20;      ↓

3\. Receive Access + Refresh Tokens

&#x20;      ↓

4\. Use Access Token for protected requests

&#x20;      ↓

5\. Access Token expires

&#x20;      ↓

6\. Send Refresh Token

&#x20;      ↓

7\. Old Refresh Token revoked

&#x20;      ↓

8\. Receive new Access + Refresh Tokens

&#x20;      ↓

9\. Continue using API

&#x20;      ↓

10\. Logout

&#x20;      ↓

11\. Refresh Token revoked

```



\---



\# 🔒 Security Considerations



Implemented:



\* bcrypt password hashing

\* JWT signature verification

\* short-lived access tokens

\* hashed refresh tokens

\* refresh-token expiration

\* refresh-token rotation

\* refresh-token revocation

\* protected routes

\* login rate limiting

\* environment-based secrets

\* PostgreSQL SSL connection



Future production improvements:



\* Redis-based distributed rate limiting

\* transactional refresh-token rotation

\* secure HttpOnly cookies for browser clients

\* CSRF protection when using cookies

\* email verification

\* password reset

\* account lockout/security monitoring

\* structured logging

\* automated tests

\* CI/CD

\* stronger password policy

\* refresh-token reuse detection

\* centralized secret management



\---



\# 📌 Project Status



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



\---



\# 👨‍💻 Author



\*\*Parth Deore\*\*



Computer Science \& Engineering



GitHub:



https://github.com/deoreparth700-design



\---



\## 📄 License



This project is intended for learning, portfolio development, and backend engineering practice.



