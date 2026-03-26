
# Realtime Room Chat API 🚀
A fully deployed **FastAPI backend** for realtime, room-based communication with **JWT authentication**.  
Features include **room discovery**, **interactive messaging**, **ImageKit.io** integration for media management (profile pics & chat media), and **Google Gemini 2.5** to generate intelligent chat summaries for new members.

🔗 **Live API / Demo**: [https://room-chat-p7bo.onrender.com/docs](https://room-chat-p7bo.onrender.com/docs)

## Key Features

*   **Real time Messaging** : Bi-directional communication using WebSockets.
*   **AI Context Summaries** : Powered by **Gemini 2.5** to catch up on the missed messages easily.
*   **Media Management** : Profile pictures and chat media handled via **ImageKit**
*   **Secure Auth** : JWT Based Authentication for user safety.
*   **Global Discovery**  : Search and join any existing chat room across the platform.
*   **Room Management** : Admin led rooms with capabilities to **kick members**, add room profile picture, update room details like description, name.
*    **Storage Optimization**: Automatic cleanup of old media; when a user updates or deletes a media file, the previous file is deleted from **ImageKit** storage to save space.

*   **Structured Backend** : Modular architecture with dedicated routers, models, and CRUD layers for scalability.

## Tech Stack

* **Framework** : FastAPI
* **Package Manager** : uv
* **AI Engine** : Google Gemini 2.5
* **Media Hosting** : ImageKit.io
* **Database**: SQLALchemy / PostgreSQL
* **Realtime** : WebSockets

## 📂 Project Structure

```text
chat/
└── app/
    ├── crud/               # DB operations (messages.py, rooms.py, users.py)
    ├── models/             # DB tables (message.py, room.py, user.py)
    ├── routers/            # API endpoints (message.py, room.py, user.py, websocket.py)
    ├── schemas/            # Pydantic validation (message.py, room.py, user.py)
    ├── ai_service.py       # Gemini 2.5 summary logic
    ├── auth.py             # Authentication handlers
    ├── db.py               # Database engine & session setup
    ├── imagekit.py         # Media upload configuration
    ├── main.py             # FastAPI app initialization
    ├── security.py         # Password hashing & JWT logic
    └── websocket_manager.py # WebSocket connection logic
├── .env                    # Environment secrets
├── pyproject.toml          # Project dependencies (uv)
└── uv.lock                 # Lockfile for consistent environments
```
## Getting Started

### 1. Clone & Install
```bash
git clone https://github.com/hrithvikcodes/realtime-room-chat.git
cd realtime-room-chat
uv sync
```
### 2. Environment Setup
Since this project uses external services, you must create a `.env` file inside the `app/` directory:

```text
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_jwt_secret_key
GEMINI_API_KEY=your_google_gemini_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_URL_ENDPOINT=https://ik.imagekit.io
```
### 3. Run the Application
```bash
uv run fastapi dev app/main.py
```
### 4. Once the Server is running, we can explore the interactive docs at:
* **Swagger UI**: http://localhost:8000/docs
* **ReDoc** : http://localhost:8000/redoc

---
Developed by [Hrithvik](https://github.com/hrithvikcodes)




