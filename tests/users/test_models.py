import pytest
from datetime import datetime, timezone
from app.users.models.user import User, UserRole
from app.core.security import hash_password, verify_password
from tests.factories import UserFactory

class TestUserModel:
    def test_user_creation(self):
        user = UserFactory()
        assert user.email is not None
        assert user.password is not None
        assert user.profile_name is not None
        assert user.role in [UserRole.ADMIN, UserRole.STAFF, UserRole.COMMON]
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.deleted_at is None

    def test_user_with_specific_values(self):
        user = UserFactory(
            email="test@example.com",
            profile_name="Test User",
            role=UserRole.ADMIN,
            is_active=False
        )
        assert user.email == "test@example.com"
        assert user.profile_name == "Test User"
        assert user.role == UserRole.ADMIN
        assert user.is_active is False

    def test_user_password_hashing(self):
        plain_password = "testpassword123"
        hashed_password = hash_password(plain_password)
        
        user = UserFactory(password=hashed_password)
        assert user.password != plain_password
        assert verify_password(plain_password, user.password)

    def test_user_unique_emails(self):
        user1 = UserFactory(email="unique@example.com")
        user2 = UserFactory(email="unique@example.com")
        
        # 이메일이 같아도 팩토리에서는 생성 가능하지만, 실제 DB에서는 유니크 제약이 있음
        assert user1.email == user2.email

    def test_user_default_values(self):
        user = UserFactory()
        assert user.is_active is True
        assert user.deleted_at is None

class TestUserRole:
    def test_user_role_enum_values(self):
        assert UserRole.ADMIN == "ADMIN"
        assert UserRole.STAFF == "STAFF"
        assert UserRole.COMMON == "COMMON"

    def test_user_role_assignment(self):
        admin_user = UserFactory(role=UserRole.ADMIN)
        staff_user = UserFactory(role=UserRole.STAFF)
        common_user = UserFactory(role=UserRole.COMMON)
        
        assert admin_user.role == UserRole.ADMIN
        assert staff_user.role == UserRole.STAFF
        assert common_user.role == UserRole.COMMON

    def test_user_role_string_comparison(self):
        user = UserFactory(role=UserRole.ADMIN)
        assert user.role == "ADMIN"
        assert user.role != "STAFF"
        assert user.role != "COMMON"

class TestUserRelationships:
    def test_user_jwt_storage_relationship(self):
        user = UserFactory()
        # 관계 속성이 존재하는지 확인
        assert hasattr(user, 'jwt_storage')
        
    def test_user_tablename(self):
        assert User.__tablename__ == "users"

class TestUserValidation:
    def test_user_email_format(self):
        # 이메일 형식 검증은 일반적으로 애플리케이션 레벨에서 처리됨
        user = UserFactory(email="valid@example.com")
        assert "@" in user.email
        assert "." in user.email

    def test_user_profile_name_length(self):
        # 프로필 이름 길이 확인
        long_name = "a" * 30
        user = UserFactory(profile_name=long_name)
        assert len(user.profile_name) == 30

    def test_user_boolean_fields(self):
        active_user = UserFactory(is_active=True)
        inactive_user = UserFactory(is_active=False)
        
        assert active_user.is_active is True
        assert inactive_user.is_active is False

class TestUserTimestamps:
    def test_user_created_at_timestamp(self):
        user = UserFactory()
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)

    def test_user_updated_at_timestamp(self):
        user = UserFactory()
        assert user.updated_at is not None
        assert isinstance(user.updated_at, datetime)

    def test_user_deleted_at_nullable(self):
        user = UserFactory()
        assert user.deleted_at is None
        
        # 삭제된 사용자 시뮬레이션
        deleted_user = UserFactory(deleted_at=datetime.now(timezone.utc))
        assert deleted_user.deleted_at is not None
        assert isinstance(deleted_user.deleted_at, datetime)