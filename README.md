# Realtime Room Chat API 🚀
A fully deployed **FastAPI backend** for realtime, room-based communication with **JWT authentication**.  
Features include **invite-only room joining**, **interactive messaging**, **ImageKit.io** integration for media management (profile pics & chat media), **Redis caching** for fast message delivery, and **Google Gemini 2.5** to generate intelligent chat summaries for new members.

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

## Tech Stack
* **Framework** : FastAPI
* **Package Manager** : uv
* **AI Engine** : Google Gemini 2.5 API
* **Media Hosting** : ImageKit.io
* **Database** : SQLAlchemy(async) + PostgreSQL
* **Cache** : Redis
* **Realtime** : WebSockets
* **Containerization** : Docker
* **Deployment** : Railway
* **Rate Limiting**: slowapo + Redis
* **Logging** : python-json-logger
* **Migrations**: alembic
* **Auth** : JWT + argon2 hashing

## 📂 Project Structure
```text
chat/
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
├── alembic.ini
├── Dockerfile
├── railway.toml
├── .env.example
├── pyproject.toml
└── uv.lock
```
***Load Testing***
Tested with Locust : 32 concurrent WebSocket connections across 4 rooms with 8 users each
**Results: **
Min response time : 462ms
Median response time: 650ms
Max response time : 1111ms
Failure rate: 0%
>Running on Railway's free tier (512 GB RAM, 1v CPU, shared). These numbers reflect that constraint. On a dedicated server with more resources, both throughput and latency would improve significantly.
>The ~200ms baseline is geographic , test machine is in India, Railway servers are in US Oregon. On a closer server  these numbers would roughly halve.

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
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=
REFRESH_TOKEN_EXPIRE_DAYS=
IMAGEKIT_PUBLIC_KEY=...
IMAGEKIT_PRIVATE_KEY=...
URL_ENDPOINT=...
GOOGLE_API_KEY=...
```

### 3. Run Migrations
```bash
uv run alembic upgrade head
```

### 4. Run the Application
```bash
uv run fastapi dev app/main.py
```

### 5. Explore the docs
* **Swagger UI**: http://localhost:8000/docs
* **ReDoc** : http://localhost:8000/redoc

### Docker
```bash
docker build -t chat-app .
docker run -p 8000:8000 --env-file .env chat-app
```

---
Developed by [Hrithvik](https://github.com/hrithvikcodes) ♡



