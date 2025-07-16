import pytest
import os
from unittest.mock import patch, MagicMock
from app.core.config import Settings

class TestSettingsInitialization:
    def test_default_settings(self):
        settings = Settings()
        assert settings.app_name == "FastAPI Boilerplate"
        assert settings.environment == "local"
        assert settings.debug is True
        assert settings.aws_region == "ap-northeast-2"
        assert settings.ssh_remote_port == 5432
        assert settings.ssh_local_port == 5432

    def test_settings_with_env_vars(self):
        with patch.dict(os.environ, {
            "APP_NAME": "Test App",
            "ENVIRONMENT": "production",
            "DEBUG": "false"
        }):
            settings = Settings()
            assert settings.app_name == "Test App"
            assert settings.environment == "production"
            assert settings.debug is False

class TestDatabaseUrlGeneration:
    def test_database_url_from_components(self):
        settings = Settings(
            db_host="localhost",
            db_port="5432",
            db_name="testdb",
            db_username="testuser",
            db_password="testpass"
        )
        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        assert settings.database_url == expected_url

    def test_database_url_direct_setting(self):
        direct_url = "postgresql://user:pass@host:5432/db"
        settings = Settings(database_url=direct_url)
        assert settings.database_url == direct_url

    def test_database_url_property(self):
        settings = Settings(database_url="postgresql://user:pass@host:5432/db")
        assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"

    def test_database_url_property_not_set(self):
        settings = Settings()
        with pytest.raises(ValueError, match="DATABASE_URL이 설정되지 않았습니다."):
            _ = settings.DATABASE_URL

class TestRedisUrlGeneration:
    def test_redis_url_from_components(self):
        settings = Settings(
            redis_host="localhost",
            redis_port=6379
        )
        assert settings.redis_url == "redis://localhost:6379"

    def test_redis_url_direct_setting(self):
        direct_url = "redis://localhost:6379"
        settings = Settings(redis_url=direct_url)
        assert settings.redis_url == direct_url

    def test_redis_url_property(self):
        settings = Settings(redis_url="redis://localhost:6379")
        assert settings.REDIS_URL == "redis://localhost:6379"

    def test_redis_url_property_not_set(self):
        settings = Settings()
        with pytest.raises(ValueError, match="REDIS_URL이 설정되지 않았습니다."):
            _ = settings.REDIS_URL

class TestSshConfiguration:
    def test_ssh_remote_host_from_database_url(self):
        settings = Settings(
            database_url="postgresql://user:pass@db.example.com:5432/dbname"
        )
        assert settings.ssh_remote_host == "db.example.com"

    def test_ssh_remote_host_from_db_host(self):
        settings = Settings(
            db_host="localhost",
            db_port="5432",
            db_name="testdb",
            db_username="testuser",
            db_password="testpass"
        )
        assert settings.ssh_remote_host == "localhost"

    def test_ssh_enabled_with_complete_config(self):
        settings = Settings(
            ssh_host="bastion.example.com",
            ssh_user="ubuntu",
            ssh_key_path="/path/to/key",
            ssh_remote_host="db.example.com"
        )
        assert settings.is_ssh is True

    def test_ssh_disabled_with_incomplete_config(self):
        settings = Settings(
            ssh_host="bastion.example.com",
            ssh_user="ubuntu"
            # ssh_key_path와 ssh_remote_host가 없음
        )
        assert settings.is_ssh is False

    @patch.dict(os.environ, {"IS_SSH": "true"})
    def test_ssh_enabled_by_env_var(self):
        settings = Settings()
        assert settings.is_ssh is True

    @patch.dict(os.environ, {"IS_SSH": "false"})
    def test_ssh_disabled_by_env_var(self):
        settings = Settings(
            ssh_host="bastion.example.com",
            ssh_user="ubuntu",
            ssh_key_path="/path/to/key",
            ssh_remote_host="db.example.com"
        )
        assert settings.is_ssh is False

class TestBastionCompatibility:
    def test_bastion_to_ssh_conversion(self):
        settings = Settings(
            bastion_host="bastion.example.com",
            bastion_username="ec2-user",
            bastion_key_file="/path/to/key"
        )
        assert settings.ssh_host == "bastion.example.com"
        assert settings.ssh_user == "ec2-user"
        assert settings.ssh_key_path == "/path/to/key"

    def test_bastion_fallback_username(self):
        settings = Settings(
            bastion_host="bastion.example.com",
            bastion_key_file="/path/to/key"
        )
        assert settings.ssh_host == "bastion.example.com"
        assert settings.ssh_user == "ubuntu"  # 기본값
        assert settings.ssh_key_path == "/path/to/key"

class TestPropertyAccess:
    def test_all_properties_accessible(self):
        settings = Settings(
            database_url="postgresql://user:pass@host:5432/db",
            redis_url="redis://localhost:6379",
            ssh_host="bastion.example.com",
            ssh_user="ubuntu",
            ssh_key_path="/path/to/key",
            ssh_remote_host="db.example.com",
            db_host="localhost",
            db_port="5432",
            db_username="user",
            db_password="pass",
            db_name="db",
            redis_host="localhost",
            redis_port=6379,
            jwt_access_secret="secret",
            jwt_access_expiration_time="3600",
            jwt_refresh_secret="refresh_secret",
            jwt_refresh_expiration_time="7200",
            jwt_admin_access_secret="admin_secret",
            jwt_admin_access_expiration_time="1800",
            aws_access_key_id="key_id",
            aws_secret_access_key="secret_key",
            aws_s3_bucket_name="bucket",
            aws_s3_cdn_url="https://cdn.example.com"
        )
        
        # 모든 프로퍼티가 접근 가능한지 확인
        assert settings.DATABASE_URL == "postgresql://user:pass@host:5432/db"
        assert settings.REDIS_URL == "redis://localhost:6379"
        assert settings.IS_SSH is True
        assert settings.SSH_HOST == "bastion.example.com"
        assert settings.SSH_USER == "ubuntu"
        assert settings.SSH_KEY_PATH == "/path/to/key"
        assert settings.SSH_REMOTE_HOST == "db.example.com"
        assert settings.SSH_REMOTE_PORT == 5432
        assert settings.SSH_LOCAL_PORT == 5432
        assert settings.DB_HOST == "localhost"
        assert settings.DB_PORT == 5432
        assert settings.DB_USERNAME == "user"
        assert settings.DB_PASSWORD == "pass"
        assert settings.DB_NAME == "db"
        assert settings.REDIS_HOST == "localhost"
        assert settings.REDIS_PORT == 6379
        assert settings.JWT_ACCESS_SECRET == "secret"
        assert settings.JWT_ACCESS_EXPIRATION_TIME == "3600"
        assert settings.JWT_REFRESH_SECRET == "refresh_secret"
        assert settings.JWT_REFRESH_EXPIRATION_TIME == "7200"
        assert settings.JWT_ADMIN_ACCESS_SECRET == "admin_secret"
        assert settings.JWT_ADMIN_ACCESS_EXPIRATION_TIME == "1800"
        assert settings.AWS_REGION == "ap-northeast-2"
        assert settings.AWS_ACCESS_KEY_ID == "key_id"
        assert settings.AWS_SECRET_ACCESS_KEY == "secret_key"
        assert settings.AWS_S3_BUCKET_NAME == "bucket"
        assert settings.AWS_S3_CDN_URL == "https://cdn.example.com"
        assert settings.NODE_ENV == "local"

class TestEnvironmentHandling:
    @patch('app.core.config.load_dotenv')
    @patch.dict(os.environ, {"ENVIRONMENT": "prod"})
    def test_production_environment(self, mock_load_dotenv):
        Settings()
        mock_load_dotenv.assert_called_with("env/.env.prod")

    @patch('app.core.config.load_dotenv')
    @patch.dict(os.environ, {"ENVIRONMENT": "staging"})
    def test_staging_environment(self, mock_load_dotenv):
        Settings()
        mock_load_dotenv.assert_called_with("env/.env.staging")

    @patch('app.core.config.load_dotenv')
    @patch.dict(os.environ, {"ENVIRONMENT": "local"})
    def test_local_environment(self, mock_load_dotenv):
        Settings()
        mock_load_dotenv.assert_called_with("env/.env.local")

    @patch('app.core.config.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_default_environment(self, mock_load_dotenv):
        Settings()
        mock_load_dotenv.assert_called_with("env/.env.local")