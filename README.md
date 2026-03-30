
# Realtime Room Chat API 🚀
A fully deployed **FastAPI backend** for realtime, room-based communication with **JWT authentication**.  
Features include **room discovery**, **interactive messaging**, **ImageKit.io** integration for media management (profile pics & chat media), and **Google Gemini 2.5** to generate intelligent chat summaries for new members.

Live URL : https://room-chat-p7bo.onrender.com/docs
## Key Features

*   **Real time Messaging** : Bi-directional communication using WebSockets.
*   **AI Context Summaries** : Powered by **Gemini 2.5** to catch up on the missed messages easily.
*   **Media Management** : Profile pictures and chat media handled via **ImageKit**
*   **Secure Auth** : JWT Based Authentication with refresh tokens saved in the databse and rotated on each use and
                      invalidated on logout which prevents reuse attacks
*   **Global Discovery**  : Search and join any existing chat room across the platform.
*   **Room Management** : Admin led rooms with capabilities to **kick members**, add room profile picture, update room   details like description, name.
*    **Storage Optimization**: Automatic cleanup of old media; when a user updates or deletes a media file, the previous file is deleted from **ImageKit** storage to save space.

*   **Structured Backend** : Modular architecture with dedicated routers, models, and CRUD layers for scalability.

## Tech Stack

* **Framework** : FastAPI
* **Package Manager** : uv
* **AI Engine** : Google Gemini 2.5
* **Media Hosting** : ImageKit.io
* **Database**: SQLALchemy + PostgreSQL
* **Realtime** : WebSockets

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
│   ├── db.py
│   ├── imagekit.py
│   ├── main.py
│   ├── security.py
│   └── websocket_manager.py
├── alembic.ini            
├── .env
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
Since this project uses external services, you must create a `.env` file inside the `app/` directory:

```text
You can refer to `.env.example` for required variables.
```
## Database Setup (Alembic)

This project uses Alembic for database migrations. Tables are NOT created automatically.

### Run migrations
```bash
alembic upgrade head
```
### 3. Run the Application
```bash
uv run fastapi dev app/main.py
```
### 4. Once the Server is running, we can explore the interactive docs at:
* **Swagger UI**: http://localhost:8000/docs
* **ReDoc** : http://localhost:8000/redoc

---
Developed by [Hrithvik](https://github.com/hrithvikcodes) ♡




