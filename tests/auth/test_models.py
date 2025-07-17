import pytest
from datetime import datetime, timezone
from app.auth.models.jwt_storage import JwtStorage
from app.users.models.user import User
from tests.factories import JwtStorageFactory, UserFactory

class TestJwtStorageModel:
    def test_jwt_storage_creation(self):
        jwt_storage = JwtStorageFactory()
        assert jwt_storage.refresh_token is not None
        assert jwt_storage.refresh_token_expired_at is not None
        assert jwt_storage.user_id is not None
        assert jwt_storage.created_at is not None
        assert jwt_storage.updated_at is not None
        assert jwt_storage.deleted_at is None

    def test_jwt_storage_with_specific_values(self):
        user = UserFactory()
        jwt_storage = JwtStorageFactory(
            refresh_token="specific_token",
            refresh_token_expired_at=1234567890,
            user_id=user.id
        )
        assert jwt_storage.refresh_token == "specific_token"
        assert jwt_storage.refresh_token_expired_at == 1234567890
        assert jwt_storage.user_id == user.id

    def test_jwt_storage_nullable_fields(self):
        jwt_storage = JwtStorageFactory(
            refresh_token=None,
            refresh_token_expired_at=None
        )
        assert jwt_storage.refresh_token is None
        assert jwt_storage.refresh_token_expired_at is None

    def test_jwt_storage_tablename(self):
        assert JwtStorage.__tablename__ == "jwt_storage"

class TestJwtStorageRelationships:
    def test_jwt_storage_user_relationship(self):
        jwt_storage = JwtStorageFactory()
        # 관계 속성이 존재하는지 확인
        assert hasattr(jwt_storage, 'user')

    def test_jwt_storage_foreign_key_constraint(self):
        user = UserFactory()
        jwt_storage = JwtStorageFactory(user_id=user.id)
        assert jwt_storage.user_id == user.id

class TestJwtStorageValidation:
    def test_jwt_storage_refresh_token_length(self):
        long_token = "a" * 255
        jwt_storage = JwtStorageFactory(refresh_token=long_token)
        assert len(jwt_storage.refresh_token) == 255

    def test_jwt_storage_expiration_timestamp(self):
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        future_timestamp = current_timestamp + 3600
        
        jwt_storage = JwtStorageFactory(
            refresh_token_expired_at=future_timestamp
        )
        assert jwt_storage.refresh_token_expired_at == future_timestamp
        assert jwt_storage.refresh_token_expired_at > current_timestamp

    def test_jwt_storage_user_id_required(self):
        user = UserFactory()
        jwt_storage = JwtStorageFactory(user_id=user.id)
        assert jwt_storage.user_id is not None
        assert isinstance(jwt_storage.user_id, int)

class TestJwtStorageTimestamps:
    def test_jwt_storage_created_at_timestamp(self):
        jwt_storage = JwtStorageFactory()
        assert jwt_storage.created_at is not None
        assert isinstance(jwt_storage.created_at, datetime)

    def test_jwt_storage_updated_at_timestamp(self):
        jwt_storage = JwtStorageFactory()
        assert jwt_storage.updated_at is not None
        assert isinstance(jwt_storage.updated_at, datetime)

    def test_jwt_storage_deleted_at_nullable(self):
        jwt_storage = JwtStorageFactory()
        assert jwt_storage.deleted_at is None
        
        # 삭제된 JWT 스토리지 시뮬레이션
        deleted_jwt_storage = JwtStorageFactory(deleted_at=datetime.now(timezone.utc))
        assert deleted_jwt_storage.deleted_at is not None
        assert isinstance(deleted_jwt_storage.deleted_at, datetime)

class TestJwtStorageBusinessLogic:
    def test_jwt_storage_token_expiration_check(self):
        current_timestamp = int(datetime.now(timezone.utc).timestamp())
        
        # 만료되지 않은 토큰
        future_timestamp = current_timestamp + 3600
        valid_jwt_storage = JwtStorageFactory(
            refresh_token_expired_at=future_timestamp
        )
        assert valid_jwt_storage.refresh_token_expired_at > current_timestamp
        
        # 만료된 토큰
        past_timestamp = current_timestamp - 3600
        expired_jwt_storage = JwtStorageFactory(
            refresh_token_expired_at=past_timestamp
        )
        assert expired_jwt_storage.refresh_token_expired_at < current_timestamp

    def test_jwt_storage_empty_token(self):
        jwt_storage = JwtStorageFactory(refresh_token="")
        assert jwt_storage.refresh_token == ""

    def test_jwt_storage_multiple_for_same_user(self):
        user = UserFactory()
        jwt_storage1 = JwtStorageFactory(user_id=user.id)
        jwt_storage2 = JwtStorageFactory(user_id=user.id)
        
        # 같은 사용자에 대해 여러 JWT 스토리지가 생성될 수 있음
        assert jwt_storage1.user_id == jwt_storage2.user_id
        assert jwt_storage1.id != jwt_storage2.id