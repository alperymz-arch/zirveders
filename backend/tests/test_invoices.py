from app.services.user_service import create_user


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(client, db_session, email: str = "invoicer@example.com") -> dict:
    create_user(db_session, email=email, password="secret123")
    token = _login(client, email, "secret123")
    return {"Authorization": f"Bearer {token}"}


def test_create_invoice_success(client, db_session):
    headers = _auth_headers(client, db_session)

    response = client.post(
        "/api/accounting/invoices",
        json={
            "customer_external_id": "C001",
            "lines": [{"aciklama": "Danışmanlık", "tutar": 100.5}],
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["external_id"].startswith("MOCK-INV-")
    assert data["customer_name"] == "Örnek Müşteri A.Ş."
    assert data["total_amount"] == 100.5


def test_create_invoice_unknown_customer(client, db_session):
    headers = _auth_headers(client, db_session, "invoicer2@example.com")

    response = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "NOPE", "lines": [{"aciklama": "x", "tutar": 10}]},
        headers=headers,
    )
    assert response.status_code == 404


def test_create_invoice_requires_at_least_one_line(client, db_session):
    headers = _auth_headers(client, db_session, "invoicer3@example.com")

    response = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": []},
        headers=headers,
    )
    assert response.status_code == 422


def test_duplicate_reference_no_is_idempotent(client, db_session):
    headers = _auth_headers(client, db_session, "invoicer4@example.com")
    payload = {
        "customer_external_id": "C001",
        "reference_no": "TEST-REF-001",
        "lines": [{"aciklama": "Ürün", "tutar": 50}],
    }

    first = client.post("/api/accounting/invoices", json=payload, headers=headers)
    second = client.post("/api/accounting/invoices", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["external_id"] == second.json()["external_id"]


def test_list_invoices_requires_auth(client):
    response = client.get("/api/accounting/invoices")
    assert response.status_code == 401


def test_list_invoices_returns_created(client, db_session):
    headers = _auth_headers(client, db_session, "invoicer5@example.com")
    client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "y", "tutar": 5}]},
        headers=headers,
    )

    response = client.get("/api/accounting/invoices", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
