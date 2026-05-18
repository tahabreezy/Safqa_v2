from unittest.mock import AsyncMock, patch


class TestRegister:
    ROUTE = "/v1/auth/register"

    def test_success(self, client, fake_user):
        with (
            patch("routers.auth.register_user", AsyncMock(return_value=fake_user)),
            patch("routers.auth.create_access_token", return_value="access-token"),
            patch("routers.auth.create_refresh_token", return_value="refresh-token"),
        ):
            resp = client.post(self.ROUTE, json={"email": "a@b.com", "password": "Secret1!"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "access-token"
        assert data["refresh_token"] == "refresh-token"
        assert data["token_type"] == "bearer"

    def test_duplicate_email_returns_409(self, client):
        with patch("routers.auth.register_user", AsyncMock(side_effect=ValueError("Email already registered"))):
            resp = client.post(self.ROUTE, json={"email": "dup@b.com", "password": "Secret1!"})

        assert resp.status_code == 409
        assert resp.json()["detail"] == "Email already registered"

    def test_invalid_email_returns_422(self, client):
        resp = client.post(self.ROUTE, json={"email": "not-an-email", "password": "Secret1!"})
        assert resp.status_code == 422


class TestLogin:
    ROUTE = "/v1/auth/login"

    def test_success(self, client, fake_user):
        with (
            patch("routers.auth.login_user", AsyncMock(return_value=fake_user)),
            patch("routers.auth.create_access_token", return_value="access-token"),
            patch("routers.auth.create_refresh_token", return_value="refresh-token"),
        ):
            resp = client.post(self.ROUTE, json={"email": "a@b.com", "password": "Secret1!"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "access-token"
        assert data["refresh_token"] == "refresh-token"

    def test_invalid_credentials_returns_401(self, client):
        with patch("routers.auth.login_user", AsyncMock(side_effect=ValueError("Invalid email or password"))):
            resp = client.post(self.ROUTE, json={"email": "a@b.com", "password": "wrong"})

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid email or password"


class TestRefresh:
    ROUTE = "/v1/auth/refresh"

    def test_success(self, client):
        with patch("routers.auth.rotate_refresh_token", AsyncMock(return_value=("new-access", "new-refresh"))):
            resp = client.post(self.ROUTE, json={"refresh_token": "valid-refresh-token"})

        assert resp.status_code == 200
        data = resp.json()
        assert data["access_token"] == "new-access"
        assert data["refresh_token"] == "new-refresh"

    def test_invalid_token_returns_401(self, client):
        with patch("routers.auth.rotate_refresh_token", AsyncMock(side_effect=Exception("Invalid token"))):
            resp = client.post(self.ROUTE, json={"refresh_token": "bad-token"})

        assert resp.status_code == 401


class TestMe:
    ROUTE = "/v1/auth/me"

    def test_returns_user(self, client, mock_get_current_user, fake_user):
        resp = client.get(self.ROUTE)

        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == fake_user["email"]
        assert data["id"] == fake_user["id"]

    def test_unauthorized_without_token(self, client):
        resp = client.get(self.ROUTE)
        assert resp.status_code == 401

    def test_unauthorized_with_bad_token(self, client):
        resp = client.get(self.ROUTE, headers={"Authorization": "Bearer bad-token"})
        assert resp.status_code == 401
