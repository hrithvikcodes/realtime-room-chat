from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app


def test_send_message(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    response = client.post(f"/messages/{room_id}/send", data={
        "content": "This is a test message..."
    }, headers=member_headers)
    assert response.status_code == 201


def test_send_message_unauthorized(client, room_with_member, outsider_headers):
    room_id, admin_headers, member_headers = room_with_member
    response = client.post(f"/messages/{room_id}/send", data={
        "content": "I shouldn't be able to send this"
    }, headers=outsider_headers)
    assert response.status_code == 403


def test_get_recent_messages(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    client.post(f"/messages/{room_id}/send", data={
        "content": "hello there"
    }, headers=member_headers)

    response = client.get(f"/messages/{room_id}/recent", headers=member_headers)
    assert response.status_code == 200


def test_get_recent_messages_unauthorized(client, room_with_member, outsider_headers):
    room_id, admin_headers, member_headers = room_with_member
    response = client.get(f"/messages/{room_id}/recent", headers=outsider_headers)
    assert response.status_code == 403


def test_get_messages_by_sender_name(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    client.post(f"/messages/{room_id}/send", data={
        "content": "message from member"
    }, headers=member_headers)

    response = client.get(f"/messages/{room_id}", params={"name": "Member"}, headers=member_headers)
    assert response.status_code == 200


def test_search_messages_by_keyword(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    client.post(f"/messages/{room_id}/send", data={
        "content": "unique searchable phrase"
    }, headers=member_headers)

    response = client.get(f"/messages/{room_id}/unique", headers=member_headers)
    assert response.status_code == 200


def test_search_messages_no_results(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    response = client.get(f"/messages/{room_id}/nonexistentkeyword123", headers=member_headers)
    assert response.status_code == 404


def test_delete_message(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    sent = client.post(f"/messages/{room_id}/send", data={
        "content": "message to delete"
    }, headers=member_headers)
    msg_id = sent.json()["id"]

    response = client.delete(f"/messages/delete/{room_id}/{msg_id}", headers=member_headers)
    assert response.status_code == 204


def test_delete_message_not_found(client, room_with_member):
    room_id, admin_headers, member_headers = room_with_member
    fake_msg_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(f"/messages/delete/{room_id}/{fake_msg_id}", headers=member_headers)
    assert response.status_code == 404