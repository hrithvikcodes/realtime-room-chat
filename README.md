# Realtime Room Chat API 🚀
A fully deployed **FastAPI backend** for realtime, room-based communication with **JWT authentication**.  
Features include **room discovery**, **interactive messaging**, **ImageKit.io** integration for media management (profile pics & chat media), **Redis caching** for fast message delivery, and **Google Gemini 2.5** to generate intelligent chat summaries for new members.

Live URL : https://your-url.up.railway.app/docs

## Key Features
*   **Real time Messaging** : Bi-directional communication using WebSockets.
*   **AI Context Summaries** : Powered by **Gemini 2.5** to catch up on missed messages easily.
*   **Message Caching** : Last 100 messages per room cached in **Redis** for fast retrieval and AI context.
*   **Media Management** : Profile pictures and chat media handled via **ImageKit**
*   **Secure Auth** : JWT Based Authentication with refresh tokens saved in the database, rotated on each use and invalidated on logout which prevents reuse attacks.
*   **Global Discovery**  : Search and join any existing chat room across the platform.
*   **Room Management** : Admin led rooms with capabilities to **kick members**, add room profile picture, update room details like description and name.
*   **Storage Optimization**: Automatic cleanup of old media; when a user updates or deletes a media file, the previous file is deleted from **ImageKit** storage to save space.
*   **Structured Backend** : Modular architecture with dedicated routers, models, and CRUD layers for scalability.

## Tech Stack
* **Framework** : FastAPI
* **Package Manager** : uv
* **AI Engine** : Google Gemini 2.5
* **Media Hosting** : ImageKit.io
* **Database** : SQLAlchemy + PostgreSQL
* **Cache** : Redis
* **Realtime** : WebSockets
* **Containerization** : Docker
* **Deployment** : Railway

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
│   ├── main.py
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



