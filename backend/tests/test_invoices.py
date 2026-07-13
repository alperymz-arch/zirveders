from app.models.invoice import Invoice
from app.models.user import UserRole
from app.services.user_service import create_user


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _auth_headers(client, db_session, email: str = "invoicer@example.com") -> dict:
    create_user(db_session, email=email, password="secret123")
    token = _login(client, email, "secret123")
    return {"Authorization": f"Bearer {token}"}


def _admin_headers(client, db_session, email: str) -> dict:
    admin = create_user(db_session, email=email, password="secret123")
    admin.role = UserRole.ADMIN
    db_session.commit()
    token = _login(client, email, "secret123")
    return {"Authorization": f"Bearer {token}"}


def _create_failed_invoice(db_session, reference_no: str) -> Invoice:
    invoice = Invoice(
        reference_no=reference_no,
        customer_external_id="C001",
        customer_name="Test",
        total_amount=10,
        currency="TRY",
        lines_json="[]",
        status="failed",
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


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


def test_cancel_sent_invoice(client, db_session):
    headers = _auth_headers(client, db_session, "cancel1@example.com")
    created = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "x", "tutar": 20}]},
        headers=headers,
    ).json()

    response = client.post(f"/api/accounting/invoices/{created['id']}/cancel", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_already_cancelled_is_conflict(client, db_session):
    headers = _auth_headers(client, db_session, "cancel2@example.com")
    created = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "x", "tutar": 20}]},
        headers=headers,
    ).json()
    client.post(f"/api/accounting/invoices/{created['id']}/cancel", headers=headers)

    response = client.post(f"/api/accounting/invoices/{created['id']}/cancel", headers=headers)
    assert response.status_code == 409


def test_cancel_not_found(client, db_session):
    headers = _auth_headers(client, db_session, "cancel3@example.com")
    response = client.post("/api/accounting/invoices/9999/cancel", headers=headers)
    assert response.status_code == 404


def test_delete_requires_admin(client, db_session):
    headers = _auth_headers(client, db_session, "regular@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-1")

    response = client.delete(f"/api/accounting/invoices/{invoice.id}", headers=headers)
    assert response.status_code == 403


def test_delete_moves_to_trash(client, db_session):
    headers = _admin_headers(client, db_session, "admin-del@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-2")

    response = client.delete(f"/api/accounting/invoices/{invoice.id}", headers=headers)
    assert response.status_code == 204

    active = client.get("/api/accounting/invoices", headers=headers).json()
    assert all(inv["id"] != invoice.id for inv in active)

    trash = client.get("/api/accounting/invoices/trash", headers=headers).json()
    assert any(inv["id"] == invoice.id for inv in trash)


def test_delete_sent_invoice_rejected(client, db_session):
    headers = _admin_headers(client, db_session, "admin-del2@example.com")
    created = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "x", "tutar": 20}]},
        headers=headers,
    ).json()

    response = client.delete(f"/api/accounting/invoices/{created['id']}", headers=headers)
    assert response.status_code == 409


def test_trash_requires_admin(client, db_session):
    headers = _auth_headers(client, db_session, "regular2@example.com")
    response = client.get("/api/accounting/invoices/trash", headers=headers)
    assert response.status_code == 403


def test_restore_from_trash(client, db_session):
    headers = _admin_headers(client, db_session, "admin-restore@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-3")
    client.delete(f"/api/accounting/invoices/{invoice.id}", headers=headers)

    response = client.post(f"/api/accounting/invoices/{invoice.id}/restore", headers=headers)
    assert response.status_code == 200
    assert response.json()["deleted_at"] is None

    active = client.get("/api/accounting/invoices", headers=headers).json()
    assert any(inv["id"] == invoice.id for inv in active)


def test_restore_not_in_trash_is_conflict(client, db_session):
    headers = _admin_headers(client, db_session, "admin-restore2@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-4")

    response = client.post(f"/api/accounting/invoices/{invoice.id}/restore", headers=headers)
    assert response.status_code == 409


def test_purge_requires_prior_delete(client, db_session):
    headers = _admin_headers(client, db_session, "admin-purge@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-5")

    response = client.delete(f"/api/accounting/invoices/{invoice.id}/purge", headers=headers)
    assert response.status_code == 409


def test_purge_permanently_removes(client, db_session):
    headers = _admin_headers(client, db_session, "admin-purge2@example.com")
    invoice = _create_failed_invoice(db_session, "FAILED-6")
    client.delete(f"/api/accounting/invoices/{invoice.id}", headers=headers)

    response = client.delete(f"/api/accounting/invoices/{invoice.id}/purge", headers=headers)
    assert response.status_code == 204

    trash = client.get("/api/accounting/invoices/trash", headers=headers).json()
    assert all(inv["id"] != invoice.id for inv in trash)


def test_update_failed_invoice_lines_resends_successfully(client, db_session):
    headers = _auth_headers(client, db_session, "editlines1@example.com")
    invoice = _create_failed_invoice(db_session, "EDIT-1")

    response = client.put(
        f"/api/accounting/invoices/{invoice.id}",
        json={"lines": [{"aciklama": "Düzeltilmiş kalem", "tutar": 75}]},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["total_amount"] == 75
    assert data["lines"] == [{"aciklama": "Düzeltilmiş kalem", "tutar": 75}]
    assert data["external_id"].startswith("MOCK-INV-")


def test_update_sent_invoice_rejected(client, db_session):
    headers = _auth_headers(client, db_session, "editlines2@example.com")
    created = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "x", "tutar": 20}]},
        headers=headers,
    ).json()

    response = client.put(
        f"/api/accounting/invoices/{created['id']}",
        json={"lines": [{"aciklama": "y", "tutar": 30}]},
        headers=headers,
    )
    assert response.status_code == 409


def test_update_cancelled_invoice_rejected(client, db_session):
    headers = _auth_headers(client, db_session, "editlines3@example.com")
    created = client.post(
        "/api/accounting/invoices",
        json={"customer_external_id": "C001", "lines": [{"aciklama": "x", "tutar": 20}]},
        headers=headers,
    ).json()
    client.post(f"/api/accounting/invoices/{created['id']}/cancel", headers=headers)

    response = client.put(
        f"/api/accounting/invoices/{created['id']}",
        json={"lines": [{"aciklama": "y", "tutar": 30}]},
        headers=headers,
    )
    assert response.status_code == 409


def test_update_deleted_invoice_rejected(client, db_session):
    headers = _admin_headers(client, db_session, "editlines-admin@example.com")
    invoice = _create_failed_invoice(db_session, "EDIT-2")
    client.delete(f"/api/accounting/invoices/{invoice.id}", headers=headers)

    response = client.put(
        f"/api/accounting/invoices/{invoice.id}",
        json={"lines": [{"aciklama": "y", "tutar": 30}]},
        headers=headers,
    )
    assert response.status_code == 409


def test_update_invoice_requires_at_least_one_line(client, db_session):
    headers = _auth_headers(client, db_session, "editlines4@example.com")
    invoice = _create_failed_invoice(db_session, "EDIT-3")

    response = client.put(
        f"/api/accounting/invoices/{invoice.id}",
        json={"lines": []},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_invoice_not_found(client, db_session):
    headers = _auth_headers(client, db_session, "editlines5@example.com")

    response = client.put(
        "/api/accounting/invoices/9999",
        json={"lines": [{"aciklama": "y", "tutar": 30}]},
        headers=headers,
    )
    assert response.status_code == 404


def test_update_invoice_requires_auth(client):
    response = client.put(
        "/api/accounting/invoices/1", json={"lines": [{"aciklama": "y", "tutar": 30}]}
    )
    assert response.status_code == 401
