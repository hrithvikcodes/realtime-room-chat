import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import uuid


@pytest.fixture
def client():
    with patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True), \
         TestClient(app) as c:
        yield c


def signup_and_login(client, email, name, password="pass123"):
    client.post("/auth/signup", json={
        "email": email,
        "name": name,
        "password": password
    })
    login = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client):
    unique_email = f"admin_{uuid.uuid4().hex[:8]}@email.com"
    return signup_and_login(client, unique_email, "Admin")


@pytest.fixture
def member_headers(client):
    unique_email = f"member_{uuid.uuid4().hex[:8]}@email.com"
    return signup_and_login(client, unique_email, "Member")


@pytest.fixture
def room_with_member(client, admin_headers, member_headers):
    """Creates a room with admin, and joins member to it. Returns (room_id, admin_headers, member_headers)."""
    room = client.post("/room/create_room", json={
        "name": f"Room {uuid.uuid4().hex[:6]}",
        "description": "test room"
    }, headers=admin_headers)
    room_id = room.json()["id"]

    invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]
    client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)

    return room_id, admin_headers, member_headers

@pytest.fixture
def outsider_headers(client):
    unique_email = f"outsider_{uuid.uuid4().hex[:8]}@email.com"
    return signup_and_login(client, unique_email, "Outsider")