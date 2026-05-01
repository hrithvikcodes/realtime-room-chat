import requests
from scripts.generate_users import INVITE_CODE

BASE_URL = "https://realtime-room-chat-production.up.railway.app"

INVITE_CODE = "dctC7jYD3gIJlnbRWx-5cw"
ROOM_ID = "e62b8074-e870-460b-a239-8faae25688bc"
users = []
for i in range(32):
    email = f"loaduser{i}@test.com"
    password = "test321"

    requests.post(f"{BASE_URL}/auth/signup", json={
        "email":email,
        "password": password,
        "name": f"user{i}"
    })

    res = requests.post(f"{BASE_URL}/auth/login", data= {
        "username": email,
        "password": password
    })

    token = res.json().get("access_token")

    requests.post(
        f"{BASE_URL}/room/{ROOM_ID}/join?invite_code={INVITE_CODE}",
        headers={"Authorization": f"Bearer {token}"},
    )

    users.append({
        "email": email,
        "password": password
    })

print(users)