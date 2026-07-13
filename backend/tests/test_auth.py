from app.services.user_service import create_user


def test_login_success(client, db_session):
    create_user(db_session, email="test@example.com", password="secret123")

    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, db_session):
    create_user(db_session, email="test@example.com", password="secret123")

    response = client.post(
        "/api/auth/login",
        data={"username": "test@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_accounting_customers_requires_auth(client, db_session):
    create_user(db_session, email="test2@example.com", password="secret123")
    login_response = client.post(
        "/api/auth/login",
        data={"username": "test2@example.com", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/accounting/customers", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
