
from fastapi.testclient import TestClient # type: ignore
from unittest.mock import patch
from app.main import app


def test_signup():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value = 1), \
         patch("limits.storage.RedisStorage.get", return_value = 0), \
         patch("limits.storage.RedisStorage.check",return_value = True):
        response = client.post("/auth/signup", json = {
            "name" : "testname",
            "email" : "uniquetest004@email.com",
            "password": "pass123"
        })

        assert response.status_code == 201

def test_signup_duplicate_email():
    with TestClient(app) as client, \
         patch("limits.storage.RedisStorage.incr", return_value = 1),\
         patch("limits.storage.RedisStorage.get", return_value = 0), \
         patch("limits.storage.RedisStorage.check", return_value = True):
        response = client.post("/auth/signup", json = {
            "name" : "testname",
            "email" : "duplicatetest002@email.com",
            "password": "pass909"
        })

        response = client.post("/auth/signup", json={
            "name": "testname",
            "email": "duplicatetest002@email.com",
            "password": "pass123"
        })

        assert response.status_code == 400


def test_login_success():
    with TestClient(app) as client,\
         patch("limits.storage.RedisStorage.incr", return_value = 1),\
         patch("limits.storage.RedisStorage.get",return_value = 0),\
         patch("limits.storage.RedisStorage.check",return_value = True):
        response = client.post("/auth/login",data = {
            "username" : "uniquetest002@email.com",
            "password" : "pass123"
        })

        assert response.status_code == 200

def test_login_invalid_credentials():
    with TestClient(app) as client,\
         patch("limits.storage.RedisStorage.incr", return_value = 1),\
         patch("limits.storage.RedisStorage.get", return_value = 0),\
         patch("limits.storage.RedisStorage.check", return_value = True):
        
        response = client.post("/auth/login",data={
            "username" : "uniquetest002@email.com",
            "password" : "pass321"
        })

        assert response.status_code == 401
        
def test_refresh_token():
    with TestClient(app) as client,\
         patch("limits.storage.RedisStorage.incr",return_value = 1),\
         patch("limits.storage.RedisStorage.get", return_value = 0),\
         patch("limits.storage.RedisStorage.check",return_value = True):
        login = client.post("auth/login", data = {
            "username": "uniquetest004@email.com",
            "password": "pass123"
        })

        refresh_token = login.json()["refresh_token"]
        response = client.post("/auth/refresh", json = {
            "refresh_token" : refresh_token,
        })

        assert response.status_code == 200


def test_logout():
    with TestClient(app) as client ,\
     patch("limits.storage.RedisStorage.incr", return_value = 1),\
     patch("limits.storage.RedisStorage.get", return_value = 0),\
     patch("limits.storage.RedisStorage.check", return_value = True):
        

        login = client.post("/auth/login",data = {
            "username" : "uniquetest004@email.com",
            "password" : "pass123"
        })
        refresh_token = login.json()["refresh_token"]
        response = client.post("/auth/logout",json = {
            "refresh_token" : refresh_token
        })

        assert response.status_code == 200