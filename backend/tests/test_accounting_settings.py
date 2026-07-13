from app.models.user import UserRole
from app.services.user_service import create_user


def _login(client, email: str, password: str) -> str:
    response = client.post("/api/auth/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _make_admin(db_session, email: str, password: str):
    user = create_user(db_session, email=email, password=password)
    user.role = UserRole.ADMIN
    db_session.commit()
    return user


def test_non_admin_cannot_read_settings(client, db_session):
    create_user(db_session, email="user@example.com", password="secret123")
    token = _login(client, "user@example.com", "secret123")

    response = client.get("/api/settings/accounting", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_can_save_and_read_masked_api_key(client, db_session):
    _make_admin(db_session, "admin@example.com", "secret123")
    token = _login(client, "admin@example.com", "secret123")
    headers = {"Authorization": f"Bearer {token}"}

    initial = client.get("/api/settings/accounting", headers=headers)
    assert initial.status_code == 200
    assert initial.json() == {"configured": False, "api_key_preview": None}

    update = client.put(
        "/api/settings/accounting", json={"api_key": "super-secret-zirapi-key-1234"}, headers=headers
    )
    assert update.status_code == 200
    assert update.json()["configured"] is True
    assert update.json()["api_key_preview"] == "****1234"
    # ham anahtar hiçbir yanıtta düz metin dönmemeli
    assert "super-secret-zirapi-key-1234" not in update.text

    after = client.get("/api/settings/accounting", headers=headers)
    assert after.json()["api_key_preview"] == "****1234"


def test_empty_api_key_rejected(client, db_session):
    _make_admin(db_session, "admin2@example.com", "secret123")
    token = _login(client, "admin2@example.com", "secret123")

    response = client.put(
        "/api/settings/accounting",
        json={"api_key": "   "},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422
