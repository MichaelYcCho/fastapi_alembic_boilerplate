import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.users.services.user_service import UserService
from app.users.dto.user_dto import UserCreateDto, UserUpdateDto, UserResponseDto, UserListResponseDto
from app.dto.base_response import BaseIdResponse, BaseResponse
from tests.factories import UserFactory
from app.users.models.user import UserRole

class TestUserRouter:
    @pytest.mark.asyncio
    async def test_create_user_success(self, client: AsyncClient):
        with patch.object(UserService, 'create_user') as mock_create:
            mock_create.return_value = BaseIdResponse(id=1, message="User created successfully")
            
            response = await client.post("/users/", json={
                "email": "test@example.com",
                "password": "testpassword123",
                "profile_name": "Test User"
            })
            
            assert response.status_code == 201
            data = response.json()
            assert data["id"] == 1
            assert data["message"] == "User created successfully"
            
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_invalid_data(self, client: AsyncClient):
        response = await client.post("/users/", json={
            "email": "invalid-email",
            "password": "short"
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_user_missing_fields(self, client: AsyncClient):
        response = await client.post("/users/", json={
            "email": "test@example.com"
            # password and profile_name missing
        })
        
        assert response.status_code == 422

class TestGetUsers:
    @pytest.mark.asyncio
    async def test_get_users_success(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'get_users_list') as mock_get_users:
                mock_get_users.return_value = UserListResponseDto(
                    users=[],
                    total=0,
                    skip=0,
                    limit=100
                )
                
                response = await client.get("/users/")
                
                assert response.status_code == 200
                data = response.json()
                assert "users" in data
                assert data["total"] == 0
                assert data["skip"] == 0
                assert data["limit"] == 100
                
                mock_get_users.assert_called_once_with(0, 100)

    @pytest.mark.asyncio
    async def test_get_users_with_pagination(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'get_users_list') as mock_get_users:
                mock_get_users.return_value = UserListResponseDto(
                    users=[],
                    total=0,
                    skip=10,
                    limit=5
                )
                
                response = await client.get("/users/?skip=10&limit=5")
                
                assert response.status_code == 200
                mock_get_users.assert_called_once_with(10, 5)

    @pytest.mark.asyncio
    async def test_get_users_unauthorized(self, client: AsyncClient):
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Unauthorized")
            
            response = await client.get("/users/")
            
            assert response.status_code == 500

class TestGetUser:
    @pytest.mark.asyncio
    async def test_get_user_success(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'get_user_by_id') as mock_get_user_by_id:
                mock_get_user_by_id.return_value = UserResponseDto(
                    id=1,
                    email="test@example.com",
                    profile_name="Test User",
                    role=UserRole.COMMON,
                    is_active=True
                )
                
                response = await client.get("/users/1")
                
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == 1
                assert data["email"] == "test@example.com"
                assert data["profile_name"] == "Test User"
                
                mock_get_user_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'get_user_by_id') as mock_get_user_by_id:
                mock_get_user_by_id.side_effect = Exception("User not found")
                
                response = await client.get("/users/999")
                
                assert response.status_code == 500

class TestUpdateUser:
    @pytest.mark.asyncio
    async def test_update_user_success(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'update_user') as mock_update:
                mock_update.return_value = UserResponseDto(
                    id=1,
                    email="updated@example.com",
                    profile_name="Updated User",
                    role=UserRole.COMMON,
                    is_active=True
                )
                
                response = await client.patch("/users/1", json={
                    "profile_name": "Updated User"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["profile_name"] == "Updated User"
                
                mock_update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_forbidden(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.patch("/users/2", json={
                "profile_name": "Updated User"
            })
            
            assert response.status_code == 403
            data = response.json()
            assert data["detail"] == "권한이 없습니다"

    @pytest.mark.asyncio
    async def test_update_user_invalid_data(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.patch("/users/1", json={
                "email": "invalid-email"
            })
            
            assert response.status_code == 422

class TestDeleteUser:
    @pytest.mark.asyncio
    async def test_delete_user_success(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'delete_user') as mock_delete:
                mock_delete.return_value = BaseResponse(message="User deleted successfully")
                
                response = await client.delete("/users/1")
                
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "User deleted successfully"
                
                mock_delete.assert_called_once_with(user)

    @pytest.mark.asyncio
    async def test_delete_user_forbidden(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.delete("/users/2")
            
            assert response.status_code == 403
            data = response.json()
            assert data["detail"] == "권한이 없습니다"

    @pytest.mark.asyncio
    async def test_delete_user_service_error(self, client: AsyncClient):
        user = UserFactory(id=1)
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(UserService, 'delete_user') as mock_delete:
                mock_delete.side_effect = Exception("Service error")
                
                response = await client.delete("/users/1")
                
                assert response.status_code == 500

class TestUserRouterValidation:
    @pytest.mark.asyncio
    async def test_get_users_invalid_skip(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.get("/users/?skip=-1")
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_users_invalid_limit(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.get("/users/?limit=0")
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_users_limit_exceeds_max(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.get("/users/?limit=101")
            
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_user_invalid_id(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            response = await client.get("/users/invalid")
            
            assert response.status_code == 422

class TestUserRouterAuth:
    @pytest.mark.asyncio
    async def test_all_protected_endpoints_require_auth(self, client: AsyncClient):
        endpoints = [
            ("GET", "/users/"),
            ("GET", "/users/1"),
            ("PATCH", "/users/1"),
            ("DELETE", "/users/1")
        ]
        
        for method, endpoint in endpoints:
            with patch('app.core.dependencies.get_current_user') as mock_get_user:
                mock_get_user.side_effect = Exception("Unauthorized")
                
                if method == "GET":
                    response = await client.get(endpoint)
                elif method == "PATCH":
                    response = await client.patch(endpoint, json={"profile_name": "test"})
                elif method == "DELETE":
                    response = await client.delete(endpoint)
                
                assert response.status_code == 500  # 인증 에러