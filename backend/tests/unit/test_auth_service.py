from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    store_refresh_token,
    is_refresh_token_valid,
    revoke_refresh_token,
)


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("mypassword")
        assert hashed != "mypassword"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("test123")
        assert verify_password("test123", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("test123")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2


class TestJWTTokens:
    def test_create_access_token(self):
        token = create_access_token("testuser", "admin")
        assert isinstance(token, str)
        assert len(token) > 50

    def test_decode_access_token(self):
        token = create_access_token("testuser", "analyst")
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "analyst"
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        token = create_refresh_token("testuser")
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("invalid.token.here") is None

    def test_expired_token(self):
        from datetime import timedelta
        token = create_access_token("user", "viewer", expires_delta=timedelta(seconds=-1))
        assert decode_token(token) is None


class TestRefreshTokenStore:
    def test_store_and_validate(self):
        token = "test-refresh-token-123"
        store_refresh_token(token)
        assert is_refresh_token_valid(token) is True

    def test_revoke_token(self):
        token = "test-revoke-token"
        store_refresh_token(token)
        revoke_refresh_token(token)
        assert is_refresh_token_valid(token) is False

    def test_nonexistent_token(self):
        assert is_refresh_token_valid("nonexistent") is False
