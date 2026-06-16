import uuid


def unique_email(prefix="user"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}@email.com"


def test_signup(client):
    response = client.post("/auth/signup", json={
        "name": "testname",
        "email": unique_email("signup"),
        "password": "pass123"
    })
    assert response.status_code == 201


def test_signup_duplicate_email(client):
    email = unique_email("dup")
    client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    response = client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    assert response.status_code == 400


def test_login_success(client):
    email = unique_email("login")
    client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": email,
        "password": "pass123"
    })
    assert response.status_code == 200


def test_login_invalid_credentials(client):
    email = unique_email("badlogin")
    client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": email,
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_refresh_token(client):
    email = unique_email("refresh")
    client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    login = client.post("/auth/login", data={
        "username": email,
        "password": "pass123"
    })
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200


def test_logout(client):
    email = unique_email("logout")
    client.post("/auth/signup", json={
        "name": "testname",
        "email": email,
        "password": "pass123"
    })
    login = client.post("/auth/login", data={
        "username": email,
        "password": "pass123"
    })
    refresh_token = login.json()["refresh_token"]

    response = client.post("/auth/logout", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200