from app.services.user_service import create_user


def _auth_headers(client, db_session, email: str) -> dict:
    create_user(db_session, email=email, password="secret123")
    response = client.post("/api/auth/login", data={"username": email, "password": "secret123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_customer_with_auto_id(client, db_session):
    headers = _auth_headers(client, db_session, "cust1@example.com")

    response = client.post(
        "/api/accounting/customers",
        json={"name": "Yeni Müşteri Ltd.", "tax_number": "1234567890"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Yeni Müşteri Ltd."
    assert data["external_id"].startswith("WEB-")
    assert data["tax_number"] == "1234567890"


def test_create_customer_with_explicit_id(client, db_session):
    headers = _auth_headers(client, db_session, "cust2@example.com")

    response = client.post(
        "/api/accounting/customers",
        json={"external_id": "C010", "name": "Belirli Kodlu Müşteri"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["external_id"] == "C010"


def test_create_customer_duplicate_id_is_conflict(client, db_session):
    headers = _auth_headers(client, db_session, "cust3@example.com")

    client.post(
        "/api/accounting/customers",
        json={"external_id": "C011", "name": "İlk"},
        headers=headers,
    )
    response = client.post(
        "/api/accounting/customers",
        json={"external_id": "C011", "name": "İkinci"},
        headers=headers,
    )
    assert response.status_code == 409


def test_create_customer_invalid_tax_number(client, db_session):
    headers = _auth_headers(client, db_session, "cust4@example.com")

    response = client.post(
        "/api/accounting/customers",
        json={"name": "Geçersiz VKN", "tax_number": "abc"},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_existing_customer(client, db_session):
    headers = _auth_headers(client, db_session, "cust5@example.com")

    response = client.put(
        "/api/accounting/customers/C001",
        json={"name": "Güncellenmiş İsim", "tax_number": "9876543210"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Güncellenmiş İsim"
    assert data["tax_number"] == "9876543210"
    # bakiye korunmalı, formdan gelmiyor
    assert data["balance"] == 1500.0


def test_update_unknown_customer(client, db_session):
    headers = _auth_headers(client, db_session, "cust6@example.com")

    response = client.put(
        "/api/accounting/customers/YOK",
        json={"name": "x"},
        headers=headers,
    )
    assert response.status_code == 404


def test_create_customer_requires_auth(client):
    response = client.post("/api/accounting/customers", json={"name": "x"})
    assert response.status_code == 401


def test_update_customer_requires_auth(client):
    response = client.put("/api/accounting/customers/C001", json={"name": "x"})
    assert response.status_code == 401
