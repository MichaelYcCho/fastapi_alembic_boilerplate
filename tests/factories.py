import factory
from factory import fuzzy
from datetime import datetime, timezone
from app.users.models.user import User, UserRole
from app.auth.models.jwt_storage import JwtStorage
from app.core.security import hash_password

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.LazyAttribute(lambda obj: hash_password("testpassword123"))
    profile_name = factory.Faker("name")
    role = fuzzy.FuzzyChoice([UserRole.ADMIN, UserRole.STAFF, UserRole.COMMON])
    is_active = True
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    deleted_at = None

class JwtStorageFactory(factory.Factory):
    class Meta:
        model = JwtStorage
    
    refresh_token = factory.Faker("uuid4")
    refresh_token_expired_at = factory.LazyFunction(lambda: int((datetime.now(timezone.utc).timestamp() + 3600)))
    user_id = factory.SubFactory(UserFactory)
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    updated_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
    deleted_at = None