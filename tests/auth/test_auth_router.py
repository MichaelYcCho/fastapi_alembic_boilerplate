import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.auth.services.auth_service import AuthService
from app.auth.dto.auth import AuthRequest, TokenResponse, AccessTokenResponse, RefreshTokenRequest
from tests.factories import UserFactory

class TestAuthRouter:
    @pytest.mark.asyncio
    async def test_sign_in_success(self, client: AsyncClient):
        # python -m pytest tests/auth/test_auth_router.py::TestAuthRouter::test_sign_in_success -v
        with patch.object(AuthService, 'login') as mock_login:
            mock_login.return_value = TokenResponse(
                access_token="test_access_token",
                refresh_token="test_refresh_token",
        
            )
            
            response = await client.post("/api/v1/auth/sign-in", json={
                "email": "test@example.com",
                "password": "testpassword"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test_access_token"
            assert data["refresh_token"] == "test_refresh_token"
            
            mock_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_sign_in_invalid_credentials(self, client: AsyncClient):
        with patch.object(AuthService, 'login') as mock_login:
            mock_login.side_effect = Exception("Invalid credentials")
            
            response = await client.post("/auth/sign-in", json={
                "email": "test@example.com",
                "password": "wrongpassword"
            })
            
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_sign_in_missing_fields(self, client: AsyncClient):
        response = await client.post("/auth/sign-in", json={
            "email": "test@example.com"
            # password missing
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_sign_in_invalid_email_format(self, client: AsyncClient):
        response = await client.post("/auth/sign-in", json={
            "email": "invalid-email",
            "password": "testpassword"
        })
        
        assert response.status_code == 422

class TestRefreshToken:
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient):
        with patch.object(AuthService, 'refresh_access_token') as mock_refresh:
            mock_refresh.return_value = AccessTokenResponse(
                access_token="new_access_token",
                token_type="bearer"
            )
            
            response = await client.post("/auth/refresh", json={
                "refresh_token": "valid_refresh_token"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "new_access_token"
            assert data["token_type"] == "bearer"
            
            mock_refresh.assert_called_once_with("valid_refresh_token")

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(self, client: AsyncClient):
        with patch.object(AuthService, 'refresh_access_token') as mock_refresh:
            mock_refresh.side_effect = Exception("Invalid refresh token")
            
            response = await client.post("/auth/refresh", json={
                "refresh_token": "invalid_refresh_token"
            })
            
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_refresh_token_missing_token(self, client: AsyncClient):
        response = await client.post("/auth/refresh", json={})
        
        assert response.status_code == 422

class TestSignOut:
    @pytest.mark.asyncio
    async def test_sign_out_success(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(AuthService, 'logout') as mock_logout:
                mock_logout.return_value = None
                
                response = await client.delete("/auth/sign-out")
                
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "success"
                
                mock_logout.assert_called_once_with(user)

    @pytest.mark.asyncio
    async def test_sign_out_unauthorized(self, client: AsyncClient):
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.side_effect = Exception("Unauthorized")
            
            response = await client.delete("/auth/sign-out")
            
            assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_sign_out_service_error(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(AuthService, 'logout') as mock_logout:
                mock_logout.side_effect = Exception("Service error")
                
                response = await client.delete("/auth/sign-out")
                
                assert response.status_code == 500

class TestAuthRouterValidation:
    @pytest.mark.asyncio
    async def test_sign_in_empty_email(self, client: AsyncClient):
        response = await client.post("/auth/sign-in", json={
            "email": "",
            "password": "testpassword"
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_sign_in_empty_password(self, client: AsyncClient):
        response = await client.post("/auth/sign-in", json={
            "email": "test@example.com",
            "password": ""
        })
        
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_refresh_token_empty_token(self, client: AsyncClient):
        response = await client.post("/auth/refresh", json={
            "refresh_token": ""
        })
        
        assert response.status_code == 422

class TestAuthRouterHeaders:
    @pytest.mark.asyncio
    async def test_sign_in_content_type(self, client: AsyncClient):
        with patch.object(AuthService, 'login') as mock_login:
            mock_login.return_value = TokenResponse(
                access_token="test_access_token",
                refresh_token="test_refresh_token",
                token_type="bearer"
            )
            
            response = await client.post("/auth/sign-in", 
                json={"email": "test@example.com", "password": "testpassword"},
                headers={"Content-Type": "application/json"}
            )
            
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_sign_out_with_auth_header(self, client: AsyncClient):
        user = UserFactory()
        
        with patch('app.core.dependencies.get_current_user') as mock_get_user:
            mock_get_user.return_value = user
            
            with patch.object(AuthService, 'logout') as mock_logout:
                mock_logout.return_value = None
                
                response = await client.delete("/auth/sign-out",
                    headers={"Authorization": "Bearer test_token"}
                )
                
                assert response.status_code == 200