# realtime-room-chat

This is a **FastAPI** backend for a realtime, room-based communication. It allows seamless user authentication, room discovery, and interactive messaging. It features ImageKit integration for media sharing, updating profile pictures and uses Gemini 2.5 to generate intelligent chat summaries, helping new members catch up on the context easily.

## Key Features

*   **Real time Messaging** : Bi-directional communication using WebSockets.
*   **AI Context Summaries** : Powered by **Gemini 2.5** to catch up on the missed messages easily.
*   **Media Management** : Profile pictures and chat media handled via **ImageKit**
*   **Secure Auth** : JWT Based Authentication for user safety.
*   **Global Discovery**  : Search and join any existing chat room across the platform.
*   **Room Management** : Admin led rooms with capabilities to **kick members**, add room profile picture, update room details like description, name.
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
{content: }
