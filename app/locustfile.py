import websocket
import json
import random
from locust import HttpUser, task, between

ROOM_IDS = [
    "a1a60304-5010-4399-a0ce-046d275a48f5",
    "563c1916-ad81-4838-be1b-67a053f1f1d0",
    "019966e1-d7a5-4a48-911a-e2d8f2b9ab8c",
    "0b8840e4-2e26-4409-a88b-62e280214ab1"
]

USERS = [
    {"email": "kalyani@gmail.com", "password": "kalyani"},
    {"email": "mahi@gmail.com", "password": "mahi"},
    {"email": "rutu@gmail.com", "password": "rutu"},
    {"email": "ananya@gmail.com", "password": "ananya"},
    {"email": "rochan@gmail.com", "password": "rochan"},
    {"email": "moksha@gmail.com", "password": "moksha"},
    {"email": "vijay@gmail.com", "password": "vijay"},
    {"email": "anu@gmail.com", "password": "anu"},
]

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        user = random.choice(USERS)
        response = self.client.post("/auth/login", data={
            "username": user["email"],
            "password": user["password"]
        })
        self.token = response.json().get("access_token")
        self.room_id = random.choice(ROOM_IDS)
        ws_url = f"wss://realtime-room-chat-production.up.railway.app/ws/{self.room_id}?token={self.token}"
        self.ws = websocket.create_connection(ws_url)

    @task
    def send_message(self):
        self.ws.send(json.dumps({"content": "hello from locust!"}))
        try:
            self.ws.recv()
        except Exception :
            pass
            
    def on_stop(self):
        self.ws.close()