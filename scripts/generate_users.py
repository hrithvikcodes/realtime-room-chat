import requests

BASE_URL = "https://realtime-room-chat-production.up.railway.app"

INVITE_CODE = "_jukwM98qqaz9M_NAA-Mvg"
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
        f"{BASE_URL}/rooms/join",
        headers={"Authorization": f"Bearer {token}"},
        json = {"invite_code": INVITE_CODE}
    )

    users.append({
        "email": email,
        "password": password
    })

print(users)