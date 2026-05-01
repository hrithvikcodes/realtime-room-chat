
import websocket
import json
import random
from locust import HttpUser, task, between
import time
from app.logger import get_logger
logger = get_logger("locustfile")
ROOM_IDS = ["e62b8074-e870-460b-a239-8faae25688bc"]
USERS = [{'email': 'loaduser0@test.com', 'password': 'test321'}, {'email': 'loaduser1@test.com', 'password': 'test321'}, {'email': 'loaduser2@test.com', 'password': 'test321'}, {'email': 'loaduser3@test.com', 'password': 'test321'}, {'email': 'loaduser4@test.com', 'password': 'test321'}, {'email': 'loaduser5@test.com', 'password': 'test321'}, {'email': 'loaduser6@test.com', 'password': 'test321'}, {'email': 'loaduser7@test.com', 'password': 'test321'}, {'email': 'loaduser8@test.com', 'password': 'test321'}, {'email': 'loaduser9@test.com', 'password': 'test321'}, {'email': 'loaduser10@test.com', 'password': 'test321'}, {'email': 'loaduser11@test.com', 'password': 'test321'}, {'email': 'loaduser12@test.com', 'password': 'test321'}, {'email': 'loaduser13@test.com', 'password': 'test321'}, {'email': 'loaduser14@test.com', 'password': 'test321'}, {'email': 'loaduser15@test.com', 'password': 'test321'}, {'email': 'loaduser16@test.com', 'password': 'test321'}, {'email': 'loaduser17@test.com', 'password': 'test321'}, {'email': 'loaduser18@test.com', 'password': 'test321'}, {'email': 'loaduser19@test.com', 'password': 'test321'}, {'email': 'loaduser20@test.com', 'password': 'test321'}, {'email': 'loaduser21@test.com', 'password': 'test321'}, {'email': 'loaduser22@test.com', 'password': 'test321'}, {'email': 'loaduser23@test.com', 'password': 'test321'}, {'email': 'loaduser24@test.com', 'password': 'test321'}, {'email': 'loaduser25@test.com', 'password': 'test321'}, {'email': 'loaduser26@test.com', 'password': 'test321'}, {'email': 'loaduser27@test.com', 'password': 'test321'}, {'email': 'loaduser28@test.com', 'password': 'test321'}, {'email': 'loaduser29@test.com', 'password': 'test321'}, {'email': 'loaduser30@test.com', 'password': 'test321'}, {'email': 'loaduser31@test.com', 'password': 'test321'}
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
            for _ in range(3):  
                start = time.time() 
                self.ws.send(json.dumps({"content": f"burst {random.randint(1,1000)}"}))
            self.ws.settimeout(3)
            try:  
                self.ws.recv()
                latency = (time.time() - start) * 1000
                logger.info("Latency: ", extra= {"Latency in ms : ": round(latency,2)})   
            except Exception as e:
                logger.error("Recieve failed",extra={"Error": str(e)})
        except Exception as e:
            logger.error("Send failed:",extra={"Error": str(e)} )  
    def on_stop(self):
        if self.ws:
            self.ws.close()