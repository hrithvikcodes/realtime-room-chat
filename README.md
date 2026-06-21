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



