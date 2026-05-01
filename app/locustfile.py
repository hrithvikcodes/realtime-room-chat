
import websocket
import json
import random
from locust import HttpUser, task, between
import time
from app.logger import get_logger
logger = get_logger("locustfile")
ROOM_IDS = [
    
    
    
    
]
USERS = [
      
]
class ChatUser(HttpUser):
    wait_time = between(0.01, 0.1)
    def on_start(self):
        self.ws = None
        user = random.choice(USERS)
        response = self.client.post("/auth/login", data={
            "username": user["email"],
            "password": user["password"]
        })
        self.token = response.json().get("access_token")
        if not self.token:
            return
        self.room_id = random.choice(ROOM_IDS)
        ws_url = f"wss://realtime-room-chat-production.up.railway.app/ws/{self.room_id}?token={self.token}"
        try:
            self.ws = websocket.create_connection(ws_url)
        except Exception as e:
            self.ws = None
    @task
    def send_message(self):
        if not self.ws:
            return   
        try:   
            self.ws.send(json.dumps({"content": "hello test 1.3!"}))
            self.ws.settimeout(3)
            try:  
                self.ws.recv()   
            except Exception:
                logger.error("Recieve failed")
        except Exception as e:
            logger.error("Send failed: %s",e,exc_info=True)  
    def on_stop(self):
        if self.ws:
            self.ws.close()