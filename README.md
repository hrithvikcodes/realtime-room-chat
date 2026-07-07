# Realtime Room Chat API 🚀
A fully deployed **FastAPI backend** for realtime, room-based communication with **JWT authentication**.  
Features include **invite only room joining**, **interactive messaging**, **ImageKit.io** integration for media management (profile pics & chat media), **Redis caching** for fast message delivery, and **Google Gemini 2.5** to generate intelligent chat summaries for new members.

Live URL : https://realtime-room-chat-production.up.railway.app/docs

## Key Features
*   **Real time Messaging** : Bi-directional communication using WebSockets.
*   **AI Context Summaries** : Powered by **Gemini 2.5** to catch up on missed messages easily.
*   **Message Caching** : Last 100 messages per room cached in **Redis** for fast retrieval and AI context.
*   **Media Management** : Profile pictures and chat media handled via **ImageKit**
*   **Secure Auth** : JWT Based Authentication with refresh tokens saved in the database, rotated on each use and invalidated on logout which prevents reuse attacks.
*   **Invite-Only Rooms**: Rooms are protected by a unique invite code. Only users with the code can join. Admins can regenerate the code at any time to invalidate old links.
*   **Room Management** : Admin led rooms with capabilities to **kick members**, add room profile picture, update room details like description and name.
*   **Storage Optimization**: Automatic cleanup of old media; when a user updates or deletes a media file, the previous file is deleted from **ImageKit** storage to save space.
*   **Structured JSON Logging** : Production grade logging across all layers (auth,rooms,messages,Websockets,HTTP middleware) with structured JSON output for easy querying.
*   **Structured Backend** : Modular architecture with dedicated routers, models, and CRUD layers for scalability.
*   **Rate limiting** : unauthenticated endpoints (login, signup) are rate limited by IP. authenticated endpoints are rate limited by user ID so VPN bypasses won't work.
*   **Automated Testing** : **26+** unit and integration tests covering auth, rooms, and messages using pytest with mocked Redis and a real PostgreSQL instance.
*   **CI/CD Pipeline** : Every push to main automatically spins up fresh PostgreSQL and Redis Containers, runs Alembic migrations, and execute all tests through GitHub Actions.
*   **Metrics & Observability**: Integrated with **Prometheus** to collect application performance metrics (request rates, latency, status codes) and **Grafana** dashboards for real time visual monitoring.

## Tech Stack
* **Framework** : FastAPI
* **Package Manager** : uv
* **AI Engine** : Google Gemini 2.5 API
* **Media Hosting** : ImageKit.io
* **Database** : SQLAlchemy(async) + PostgreSQL
* **Cache** : Redis
* **Realtime** : WebSockets
* **Containerization** : Docker + Docker Compose
* **Deployment** : Railway
* **Rate Limiting**: slowapi + Redis
* **Logging** : python-json-logger
* **Migrations**: alembic
* **Auth** : JWT + argon2 hashing
* **Testing** : pytest, pytest-asyncio, httpx
* **CI/CD** : GitHub Actions
* **Monitoring & Observability**: Prometheus + Grafana for tracking API metrics, request latencies, error rates and system performance.

## 📂 Project Structure
```text
chat/
├── .github/
│   └── workflows/
│       └── ci.yml
├── migrations/
│   ├── versions/
│   └── env.py
├── app/
│   ├── crud/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── ai_service.py
│   ├── auth.py
│   ├── chat_cache.py
│   ├── db.py
│   ├── imagekit.py
│   ├── limiter.py
│   ├── logger.py
│   ├── main.py
│   ├── middleware.py
│   ├── redis_client.py
│   ├── security.py
│   └── websocket_manager.py
├── tests/
│   ├── conftest.py
│   ├── test_user.py
│   ├── test_room.py
│   └── test_message.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── .env.example
├── pyproject.toml
└── uv.lock
```
## 🔌 API Endpoints Reference

### 🔐 Authentication & Profile (`/auth`)

All authentication endpoints utilize strict JWT token rotation (Access + Refresh tokens) and server-side rate-limiting to mitigate brute-force and credential-stuffing attacks.

| Method | Endpoint | Auth Required | Rate Limit | Description |
| :--- | :--- | :---: | :---: | :--- |
| **POST** | `/auth/signup` | ❌ None | 5/min | Registers a new user account. |
| **POST** | `/auth/login` | ❌ None | 10/min | Authenticates credentials via form data; invalidates old refresh tokens and issues a fresh token pair. |
| **POST** | `/auth/refresh` | ❌ None | 10/min | Validates and destroys the used refresh token, rotating to a new access/refresh pair. |
| **POST** | `/auth/logout` | ❌ None | ❌ None | Revokes and deletes the active refresh token session from the database. |
| **PATCH**| `/auth/profile/picture` | 🔒 JWT Bearer | ❌ None | Uploads a profile image file, replaces any existing image on ImageKit, and updates user profile strings. |
| **DELETE**| `/auth/profile/picture`| 🔒 JWT Bearer | ❌ None | Deletes the hosted avatar from ImageKit and clears references from the database. Returns `204 No Content`. |

---

### 💬 Room Management (`/room`)

All room endpoints require a valid JWT Bearer Token in the header. Administrative routes enforce internal `ADMIN` role checks.

| Method | Endpoint | Auth Required | Role Enforced | Rate Limit | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **POST** | `/room/create_room` | 🔒 JWT | None | ❌ None | Creates a new chat room and designates the creator as `ADMIN`. |
| **GET** | `/room/my-rooms` | 🔒 JWT | None | ❌ None | Fetches all chat rooms the current user belongs to. |
| **GET** | `/room/{room_id}/members` | 🔒 JWT | Member | ❌ None | Returns a list of all active participants inside the specified room. |
| **POST** | `/room/{room_id}/join` | 🔒 JWT | None | 100/min | Joins a room using a required query parameter `invite_code`. |
| **DELETE**| `/room/{room_id}/leave` | 🔒 JWT | Member | ❌ None | Removes the current user from the specified room membership. |
| **GET** | `/room/{room_id}/invite` | 🔒 JWT | Member | ❌ None | Retrieves the current active alphanumeric invitation code for the room. |
| **PUT** | `/room/{room_id}/update-details` | 🔒 JWT | **ADMIN** | ❌ None | Updates the core settings and details of a room. |
| **PUT** | `/room/{room_id}/invite/regenerate`| 🔒 JWT | **ADMIN** | ❌ None | Invalidates the old invitation code and rotates a brand new one. |
| **DELETE**| `/room/{room_id}/remove/{target_user_id}`| 🔒 JWT | **ADMIN** | ❌ None | Kicks a member from the room. Admins cannot kick other admins. |
| **DELETE**| `/room/{room_id}/delete` | 🔒 JWT | **ADMIN** | ❌ None | Destroys the room and all its cascading records from the database. |
| **PATCH**| `/room/{room_id}/profile/picture`| 🔒 JWT | **ADMIN** | ❌ None | Uploads and registers a room avatar image using ImageKit. |
| **DELETE**| `/room/{room_id}/profile/picture`| 🔒 JWT | **ADMIN** | ❌ None | Clears the room avatar from ImageKit and database storage. |
| **GET** | `/room/{room_id}/summary` | 🔒 JWT | Member | **5/hour** | **AI Catch-Up:** Pulls conversation history from Redis and pipes it to **Google Gemini AI** to produce an automated room recap. |

---

### ✉️ Message Management (`/messages`)

All message endpoints require a valid JWT Bearer Token and verify that the requesting user is an active member of the designated chat room.

| Method | Endpoint | Data Format | Pagination Parameters | Description |
| :--- | :--- | :---: | :---: | :--- |
| **POST** | `/messages/{room_id}/send` | `multipart/form-data` | None | Sends a chat message. Accepts text `content` and an optional media `file` (uploaded via ImageKit). Automatically pushes to **Redis Cache** and broadcasts to the room via **WebSockets**. |
| **GET** | `/messages/{room_id}/recent` | JSON | `limit` (1-100), `offset` | Fetches recent messages. Hits **Redis Cache** first for ultra-fast delivery, falling back to PostgreSQL if the cache is cold. |
| **GET** | `/messages/{room_id}` | JSON | `limit` (1-100), `offset` | Searches and filters a room's history to retrieve messages sent by a specific user's `name`. |
| **GET** | `/messages/{room_id}/{key_word}` | JSON | `limit` (1-100), `offset` | Performs a keyword text search across all historical messages in a given room. |
| **PUT** | `/messages/edit/{room_id}/{msg_id}` | `multipart/form-data` | None | Modifies an existing message's text, deletes the old attachment from ImageKit, and uploads a replacement file. |
| **DELETE**| `/messages/delete/{room_id}/{msg_id}` | None | None | Deletes a message from the database ("unsend") and automatically destroys associated media files on ImageKit. Returns `204 No Content`. |

---

### ⚡ Real-Time WebSockets (`/ws`)

| Protocol | Endpoint | Auth Mechanism | Handshake Validation | Description |
| :--- | :--- | :---: | :---: | :--- |
| **WS** | `/ws/{room_id}` | `token` (Query Param) | JWT + Room Existence Check | Establishes a live bidirectional chat stream. Parses incoming JSON, commits text messages to PostgreSQL asynchronously, syncs to Redis Cache, and broadcasts payloads to all active socket channels in the room. |

#### 🔑 Connection Close Status Codes
If the handshake or streaming fails, the server terminates the socket with specific WebSocket Close Codes:
*   **`403`**: Authentication/Token validation failed during connection initiation.
*   **`1008` (Policy Violation)**: The connection token is valid, but the requested `room_id` does not exist in the database.
*   **`1001` (Going Away)**: Graceful client disconnection (e.g., user closing the chat tab).

#### 📦 Client JSON Data Contract

**Incoming Frame (Client ➡️ Server):**
```json
{
  "content": "Hello, everyone!"
}
```
**Broadcasted Frame (Server ➡️ All Room Members):
```
{
  "sender": "John Doe",
  "content": "Hello, everyone!",
  "created_at": "2026-07-07 11:32:00.123456",
  "media_url": null
}

```


**Scaling note : **
The current WebSocket manager keeps connections in memory on a single server. This works well for the current scale but wouldn't support horizontal scaling. The fix would be replacing the in memory manager with Redis Pub/Sub so multiple server instances can share connections, that's on the roadmap.

## Getting Started
### 1. Clone & Install
```bash
git clone https://github.com/hrithvikcodes/realtime-room-chat.git
cd realtime-room-chat
uv sync
```

### 2. Environment Setup
Create a `.env` file in the project root. Refer to `.env.example` for required variables:
```text
DATABASE_URL= postgresql+asyncpg://postgres:yourpassword@postgres-db:5432/chat
REDIS_URL=redis://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
IMAGEKIT_PUBLIC_KEY=...
IMAGEKIT_PRIVATE_KEY=...
URL_ENDPOINT=...
GOOGLE_API_KEY=...
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=chat
```

### 3. Start all containers
```bash
docker-compose up -d
```

### 4. Run migrations
```bash
docker-compose exec fastapi uv run alembic upgrade head
```

### 5. Explore the docs
* **Swagger UI**: http://localhost:8000/docs
* **ReDoc** : http://localhost:8000/redoc

### Testing
* The project has a test suite covering authentication, room management, messaging, with Redis mocked and a real PostgreSQL test database for integration level coverage.

* Run the full tests locally inside the container:
```
 docker-compose exec fastapi uv run pytest tests/ -v
```
### CI/CD
* A GitHub Actions workflow runs automatically on every push and pull request to   main. It spins up temporary PostgreSQL and Redis service containers, installs    dependencies with uv, applies all Alembic migrations against a fresh database,   and runs the full pytest suite , catching schema or logic regressions            before they reach production.
* The workflow configuration lives in .github/workflows/ci.yml.


Developed by [Hrithvik](https://github.com/hrithvikcodes) ♡



