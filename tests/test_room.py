import uuid


def unique_room_name(prefix="Room"):
    return f"{prefix}_{uuid.uuid4().hex[:6]}"


def test_create_room(client, admin_headers):
    response = client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "Room description"
    }, headers=admin_headers)
    assert response.status_code == 201


def test_create_room_unauthorized(client):
    response = client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "Room description"
    })
    assert response.status_code == 401


def test_update_room_details(client, admin_headers):
    create_room = client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "original description"
    }, headers=admin_headers)
    room_id = create_room.json()["id"]

    response = client.put(f"/room/{room_id}/update-details", json={
        "name": unique_room_name("Updated"),
        "description": "updated description"
    }, headers=admin_headers)
    assert response.status_code == 200


def test_room_valid_invite(client, admin_headers, member_headers):
    create_room = client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "test room"
    }, headers=admin_headers)
    room_id = create_room.json()["id"]
    invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

    response = client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
    assert response.status_code == 200


def test_room_invalid_invite(client, admin_headers):
    room_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(f"/room/{room_id}/join", params={
        "invite_code": "invalidcode"
    }, headers=admin_headers)
    assert response.status_code == 404


def test_join_room_alreadymember(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    invite_code = client.get(f"/room/{room_id}/invite", headers=admin_headers).json()["invite_code"]

    # member already joined via room_with_member fixture.... 
    response = client.post(f"/room/{room_id}/join", params={"invite_code": invite_code}, headers=member_headers)
    assert response.status_code == 400


def test_get_my_rooms(client, admin_headers):
    client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "test room"
    }, headers=admin_headers)

    response = client.get("/room/my-rooms", headers=admin_headers)
    assert response.status_code == 200


def test_get_my_room_members(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    response = client.get(f"/room/{room_id}/members", headers=admin_headers)
    assert response.status_code == 200


def test_leave_room(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    response = client.delete(f"/room/{room_id}/leave", headers=member_headers)
    assert response.status_code == 204

def test_kick_member(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    members = client.get(f"/room/{room_id}/members", headers=admin_headers).json()
    kick_user_id = next(m["user_id"] for m in members if m["role"] == "member")
    response = client.delete(f"/room/{room_id}/remove/{kick_user_id}", headers=admin_headers)
    assert response.status_code == 204


def test_delete_room(client, admin_headers):
    room = client.post("/room/create_room", json={
        "name": unique_room_name(),
        "description": "test room"
    }, headers=admin_headers)
    room_id = room.json()["id"]
    response = client.delete(f"/room/{room_id}/delete", headers=admin_headers)
    assert response.status_code == 204