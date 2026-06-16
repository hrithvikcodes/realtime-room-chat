from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

def test_create_room():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        client.post("/auth/signup", json={
            "email": "adminroomA@email.com",
            "name": "Admin A",
            "password": "pass123"
        })
        login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        response = client.post("/room/create_room", json={
            "name": "Room Alpha",
            "description": "Room Alpha description"
        }, headers=headers)
        assert response.status_code == 201

def test_create_room_unauthorized():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        response = client.post("/room/create_room", json={
            "name": "Room Beta",
            "description": "Room Beta description"
        })
        assert response.status_code == 401

def test_update_room_details():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        create_room = client.post("/room/create_room", json={
            "name": "Room Gamma",
            "description": "Room Gamma description"
        }, headers=headers)
        room_id = create_room.json()["id"]
        response = client.put(f"/room/{room_id}/update-details", json={
            "name": "Room Gamma Updated",
            "description": "Updated description"
        }, headers=headers)
        assert response.status_code == 200

def test_room_valid_invite():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        client.post("/auth/signup", json={
            "email": "adminroomB@email.com",
            "name": "Admin B",
            "password": "pass123"
        })
        admin_login = client.post("/auth/login", data={
            "username": "adminroomB@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        create_room = client.post("/room/create_room", json={
            "name": "Room Delta",
            "description": "Room Delta description"
        }, headers=admin_headers)
        room_id = create_room.json()["id"]
        invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

        client.post("/auth/signup", json={
            "email": "memberroomA@email.com",
            "name": "Member A",
            "password": "pass123"
        })
        member_login = client.post("/auth/login", data={
            "username": "memberroomA@email.com",
            "password": "pass123"
        })
        member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}
        response = client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
        assert response.status_code == 200

def test_room_invalid_invite():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        room_id = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/room/{room_id}/join", params={
            "invite_code": "invalidcode"
        }, headers=headers)
        assert response.status_code == 404

def test_join_room_alreadymember():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        admin_login = client.post("/auth/login", data={
            "username": "adminroomB@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        create_room = client.post("/room/create_room", json={
            "name": "Room Epsilon",
            "description": "Room Epsilon description"
        }, headers=admin_headers)
        room_id = create_room.json()["id"]
        invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

        member_login = client.post("/auth/login", data={
            "username": "memberroomA@email.com",
            "password": "pass123"
        })
        member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}
        client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
        response = client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
        assert response.status_code == 400

def test_get_my_rooms():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        response = client.get("/room/my-rooms", headers=headers)
        assert response.status_code == 200

def test_get_my_room_members():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        admin_login = client.post("/auth/login", data={
            "username": "adminroomB@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        create_room = client.post("/room/create_room", json={
            "name": "Room Zeta",
            "description": "Room Zeta description"
        }, headers=admin_headers)
        room_id = create_room.json()["id"]
        response = client.get(f"/room/{room_id}/members", headers=admin_headers)
        assert response.status_code == 200

def test_leave_room():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        admin_login = client.post("/auth/login", data={
            "username": "adminroomB@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        room = client.post("/room/create_room", json={
            "name": "Room Eta",
            "description": "Room Eta description"
        }, headers=admin_headers)
        room_id = room.json()["id"]
        invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

        client.post("/auth/signup", json={
            "email": "memberroomB@email.com",
            "name": "Member B",
            "password": "pass123"
        })
        member_login = client.post("/auth/login", data={
            "username": "memberroomB@email.com",
            "password": "pass123"
        })
        member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}
        client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
        response = client.delete(f"/room/{room_id}/leave", headers=member_headers)
        assert response.status_code == 204

def test_kick_member():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        admin_login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        room = client.post("/room/create_room", json={
            "name": "Room Theta",
            "description": "Room Theta description"
        }, headers=admin_headers)
        room_id = room.json()["id"]
        invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

        client.post("/auth/signup", json={
            "email": "kickmeroomA@email.com",
            "name": "Kick Me A",
            "password": "pass123"
        })
        member_login = client.post("/auth/login", data={
            "username": "kickmeroomA@email.com",
            "password": "pass123"
        })
        member_headers = {"Authorization": f"Bearer {member_login.json()['access_token']}"}
        client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)

        members = client.get(f"/room/{room_id}/members", headers=admin_headers).json()
        kick_user_id = next(m["user_id"] for m in members if m["user"]["email"] == "kickmeroomA@email.com")

        response = client.delete(f"/room/{room_id}/remove/{kick_user_id}", headers=admin_headers)
        assert response.status_code == 204

def test_delete_room():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value=1), \
         patch("limits.storage.RedisStorage.get", return_value=0), \
         patch("limits.storage.RedisStorage.check", return_value=True):
        admin_login = client.post("/auth/login", data={
            "username": "adminroomA@email.com",
            "password": "pass123"
        })
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
        room = client.post("/room/create_room", json={
            "name": "Room Iota",
            "description": "Room Iota description"
        }, headers=admin_headers)
        room_id = room.json()["id"]
        response = client.delete(f"/room/{room_id}/delete", headers=admin_headers)
        assert response.status_code == 204