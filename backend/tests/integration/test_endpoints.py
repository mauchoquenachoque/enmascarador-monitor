import pytest


class TestHealthEndpoints:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

    def test_ready(self, client):
        res = client.get("/ready")
        assert res.status_code == 200
        assert res.json()["status"] == "ready"


class TestAuthEndpoints:
    def test_login_success(self, client):
        from app.core.security import hash_password
        from app.models.user import User
        from app.core.dependencies import SessionLocal

        db = SessionLocal()
        admin = User(
            username="logintest",
            email="logintest@test.com",
            hashed_password=hash_password("Pass1234!"),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.close()

        res = client.post(
            "/api/v1/auth/login",
            json={"username": "logintest", "password": "Pass1234!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_credentials(self, client):
        res = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "wrong"},
        )
        assert res.status_code == 401

    def test_me_endpoint(self, client, admin_token):
        res = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 200
        assert res.json()["username"] == "testadmin"

    def test_me_without_token(self, client):
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 403

    def test_register_requires_admin(self, client, analyst_token):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@test.com",
                "password": "Pass1234!",
                "role": "viewer",
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert res.status_code == 403

    def test_register_as_admin(self, client, admin_token):
        res = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser2",
                "email": "new2@test.com",
                "password": "Pass1234!",
                "role": "viewer",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 201
        assert res.json()["username"] == "newuser2"

    def test_refresh_token(self, client):
        from app.core.security import hash_password
        from app.models.user import User
        from app.core.dependencies import SessionLocal

        db = SessionLocal()
        user = User(
            username="refreshtest",
            email="refresh@test.com",
            hashed_password=hash_password("Pass1234!"),
            role="viewer",
        )
        db.add(user)
        db.commit()
        db.close()

        login_res = client.post(
            "/api/v1/auth/login",
            json={"username": "refreshtest", "password": "Pass1234!"},
        )
        refresh_token = login_res.json()["refresh_token"]

        res = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert res.status_code == 200
        assert "access_token" in res.json()


class TestDatabaseEndpoints:
    def test_list_engines(self, client, admin_token):
        res = client.get(
            "/api/v1/databases/engines",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "engines" in data
        assert "sqlite" in data["engines"]

    def test_list_engines_requires_auth(self, client):
        res = client.get("/api/v1/databases/engines")
        assert res.status_code == 403


class TestMaskingEndpoints:
    def test_list_algorithms(self, client, viewer_token):
        res = client.get(
            "/api/v1/masking/algorithms",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "algorithms" in data
        assert len(data["algorithms"]) >= 4

    def test_apply_masking(self, client, analyst_token):
        res = client.post(
            "/api/v1/masking/apply",
            json={
                "data": [
                    {"name": "Juan Perez", "email": "juan@test.com"},
                    {"name": "Maria Lopez", "email": "maria@test.com"},
                ],
                "rules": {"name": "redaccion", "email": "hashing"},
            },
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["rows_processed"] == 2
        assert data["masked_data"][0]["name"] == "XXXXXXXXXX"
        assert data["masked_data"][0]["email"].endswith("...")

    def test_apply_masking_all_algorithms(self, client, analyst_token):
        for alg in ["redaccion", "hashing", "encriptacion", "fpe"]:
            res = client.post(
                "/api/v1/masking/apply",
                json={
                    "data": [{"col": "testdata"}],
                    "rules": {"col": alg},
                },
                headers={"Authorization": f"Bearer {analyst_token}"},
            )
            assert res.status_code == 200, f"Failed for algorithm: {alg}"

    def test_apply_masking_viewer_cannot(self, client, viewer_token):
        res = client.post(
            "/api/v1/masking/apply",
            json={"data": [{"col": "test"}], "rules": {"col": "redaccion"}},
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 403


class TestMetricsEndpoints:
    def test_live_metrics(self, client, viewer_token):
        res = client.get(
            "/api/v1/metrics/live",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "cpu_percent" in data
        assert "ram_mb" in data

    def test_metrics_history(self, client, viewer_token):
        res = client.get(
            "/api/v1/metrics/history",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 200

    def test_metrics_summary(self, client, viewer_token):
        res = client.get(
            "/api/v1/metrics/summary",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 200


class TestDashboardEndpoints:
    def test_dashboard_stats(self, client, viewer_token):
        res = client.get(
            "/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert res.status_code == 200
        data = res.json()
        assert "total_queries" in data
        assert "total_benchmarks" in data
        assert "avg_db_latency_ms" in data
