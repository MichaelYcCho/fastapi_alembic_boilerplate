import pytest
from datetime import datetime, timedelta, timezone
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    _parse_expiration_time,
)
from app.core.config import settings

class TestPasswordHashing:
    def test_hash_password(self):
        password = "test_password"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        password = "test_password"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        password = "test_password"
        hashed = hash_password(password)
        assert verify_password("", hashed) is False

class TestExpirationTimeParsing:
    def test_parse_expiration_time_with_seconds(self):
        result = _parse_expiration_time("3600s")
        assert result == 3600

    def test_parse_expiration_time_with_number_only(self):
        result = _parse_expiration_time("7200")
        assert result == 7200

    def test_parse_expiration_time_empty_string(self):
        result = _parse_expiration_time("")
        assert result == 3600

    def test_parse_expiration_time_none(self):
        result = _parse_expiration_time(None)
        assert result == 3600

    def test_parse_expiration_time_invalid_format(self):
        result = _parse_expiration_time("invalid")
        assert result == 3600

class TestTokenGeneration:
    def test_create_access_token(self):
        data = {"sub": "user123", "name": "Test User"}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        data = {"sub": "user123", "name": "Test User"}
        token = create_refresh_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_custom_data(self):
        data = {"sub": "user123", "role": "admin", "permissions": ["read", "write"]}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)

class TestTokenVerification:
    def test_verify_valid_access_token(self):
        data = {"sub": "user123", "name": "Test User"}
        token = create_access_token(data)
        
        payload = verify_token(token, settings.JWT_ACCESS_SECRET)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["name"] == "Test User"
        assert "exp" in payload

    def test_verify_valid_refresh_token(self):
        data = {"sub": "user123", "name": "Test User"}
        token = create_refresh_token(data)
        
        payload = verify_token(token, settings.JWT_REFRESH_SECRET)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["name"] == "Test User"
        assert "exp" in payload

    def test_verify_invalid_token(self):
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token, settings.JWT_ACCESS_SECRET)
        assert payload is None

    def test_verify_token_with_wrong_secret(self):
        data = {"sub": "user123", "name": "Test User"}
        token = create_access_token(data)
        
        payload = verify_token(token, "wrong_secret")
        assert payload is None

    def test_verify_empty_token(self):
        payload = verify_token("", settings.JWT_ACCESS_SECRET)
        assert payload is None

    def test_verify_none_token(self):
        payload = verify_token(None, settings.JWT_ACCESS_SECRET)
        assert payload is None

class TestTokenExpiration:
    def test_token_contains_expiration(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        payload = verify_token(token, settings.JWT_ACCESS_SECRET)
        assert payload is not None
        assert "exp" in payload
        
        # 토큰 만료 시간이 현재 시간보다 미래인지 확인
        exp_timestamp = payload["exp"]
        current_timestamp = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > current_timestamp

    def test_access_and_refresh_token_different_expiration(self):
        data = {"sub": "user123"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = verify_token(access_token, settings.JWT_ACCESS_SECRET)
        refresh_payload = verify_token(refresh_token, settings.JWT_REFRESH_SECRET)
        
        # 일반적으로 리프레시 토큰이 액세스 토큰보다 더 오래 유지되어야 함
        assert access_payload["exp"] != refresh_payload["exp"]

class TestTokenDataIntegrity:
    def test_token_preserves_original_data(self):
        original_data = {
            "sub": "user123",
            "name": "Test User",
            "email": "test@example.com",
            "role": "user"
        }
        
        token = create_access_token(original_data)
        payload = verify_token(token, settings.JWT_ACCESS_SECRET)
        
        assert payload is not None
        for key, value in original_data.items():
            assert payload[key] == value

    def test_token_with_empty_data(self):
        data = {}
        token = create_access_token(data)
        payload = verify_token(token, settings.JWT_ACCESS_SECRET)
        
        assert payload is not None
        assert "exp" in payload
        assert len(payload) == 1  # exp만 포함되어야 함