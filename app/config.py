import os
import logging
from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import ConfigDict
import re
from dotenv import load_dotenv

# 로거 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
environment = os.getenv("ENVIRONMENT", "local")
print(f"environment: {environment}")

if environment == "prod":
    load_dotenv("env/.env.prod")
    logger.info("Production 환경 설정 로드")
elif environment == "staging":
    load_dotenv("env/.env.staging")
    logger.info("Staging 환경 설정 로드")
else:
    load_dotenv("env/.env.local")
    logger.info("Local 환경 설정 로드")

class Settings(BaseSettings):
    # 기본 설정
    app_name: str = "FastAPI Boilerplate"
    environment: str = "local"
    debug: bool = True

    # 데이터베이스 설정
    database_url: Optional[str] = None

    # 기존 NestJS 스타일 DB 설정도 지원 (자동 변환)
    dbms: Optional[str] = None
    db_host: Optional[str] = None
    db_port: Optional[str] = None
    db_name: Optional[str] = None
    db_username: Optional[str] = None
    db_password: Optional[str] = None

    # Redis 설정
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    redis_url: Optional[str] = None

    # JWT 설정
    jwt_access_secret: Optional[str] = None
    jwt_access_expiration_time: Optional[str] = None
    jwt_refresh_secret: Optional[str] = None
    jwt_refresh_expiration_time: Optional[str] = None
    jwt_admin_access_secret: Optional[str] = None
    jwt_admin_access_expiration_time: Optional[str] = None

    # AWS S3 설정
    aws_region: str = "ap-northeast-2"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket_name: Optional[str] = None
    aws_s3_cdn_url: Optional[str] = None

    # SSH 터널링 설정
    is_ssh: bool = False
    ssh_host: Optional[str] = None
    ssh_user: Optional[str] = None
    ssh_key_path: Optional[str] = None
    ssh_remote_host: Optional[str] = None
    ssh_remote_port: int = 5432
    ssh_local_port: int = 5433

    # 기존 NestJS 스타일 bastion 설정도 지원
    bastion_host: Optional[str] = None
    bastion_port: Optional[str] = None
    bastion_username: Optional[str] = None
    bastion_key_file: Optional[str] = None

    model_config = ConfigDict(
        env_file=(
            "env/.env.local" if os.getenv("ENVIRONMENT", "local") == "local" else None
        ),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("흠", os.getenv("ENVIRONMENT"), os.getenv("IS_SSH"))

        # 환경 변수에서 직접 읽기 (fallback)
        self.ssh_host = self.ssh_host or os.getenv("SSH_HOST")
        self.ssh_user = self.ssh_user or os.getenv("SSH_USER")
        self.ssh_key_path = self.ssh_key_path or os.getenv("SSH_KEY_PATH")
        self.ssh_remote_host = self.ssh_remote_host or os.getenv("SSH_REMOTE_HOST")

        # 기존 NestJS 스타일 환경 변수도 체크
        self.bastion_host = self.bastion_host or os.getenv("BASTION_HOST")
        self.bastion_username = self.bastion_username or os.getenv("BASTION_USERNAME")
        self.bastion_key_file = self.bastion_key_file or os.getenv("BASTION_KEY_FILE")

        # 기존 NestJS 설정을 FastAPI 스타일로 변환
        if not self.database_url and all(
            [
                self.db_host,
                self.db_port,
                self.db_name,
                self.db_username,
                self.db_password,
            ]
        ):
            self.database_url = f"postgresql://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

        # Redis URL 생성
        if not self.redis_url and self.redis_host and self.redis_port:
            self.redis_url = f"redis://{self.redis_host}:{self.redis_port}"

        # SSH_REMOTE_HOST가 없으면 DATABASE_URL에서 호스트 추출 또는 DB_HOST 사용
        if not self.ssh_remote_host:
            if self.database_url:
                # postgresql://user:pass@host:port/db 형태에서 host 추출
                match = re.search(r"@([^:]+):", self.database_url)
                if match:
                    self.ssh_remote_host = match.group(1)
            elif self.db_host:
                self.ssh_remote_host = self.db_host

        # 기존 NestJS 설정을 SSH 설정으로 변환
        if not self.ssh_host and self.bastion_host:
            self.ssh_host = self.bastion_host
            self.ssh_user = self.bastion_username or "ubuntu"
            self.ssh_key_path = self.bastion_key_file

        # SSH 사용 여부 결정 - 환경변수 IS_SSH를 우선적으로 확인
        env_is_ssh = os.getenv("IS_SSH", "false").lower()
        if env_is_ssh in ["true", "1", "yes"]:
            self.is_ssh = True
        elif env_is_ssh in ["false", "0", "no"]:
            self.is_ssh = False
        else:
            # 환경변수가 없거나 명확하지 않은 경우, SSH 설정이 완전한지 확인
            if self.ssh_host and self.ssh_user and self.ssh_key_path and self.ssh_remote_host:
                self.is_ssh = True
            else:
                self.is_ssh = False

    @property
    def DATABASE_URL(self) -> str:
        if not self.database_url:
            raise ValueError("DATABASE_URL이 설정되지 않았습니다.")
        return self.database_url

    @property
    def REDIS_URL(self) -> str:
        if not self.redis_url:
            raise ValueError("REDIS_URL이 설정되지 않았습니다.")
        return self.redis_url

    @property
    def IS_SSH(self) -> bool:
        return self.is_ssh

    @property
    def SSH_HOST(self) -> Optional[str]:
        return self.ssh_host

    @property
    def SSH_USER(self) -> Optional[str]:
        return self.ssh_user

    @property
    def SSH_KEY_PATH(self) -> Optional[str]:
        return self.ssh_key_path

    @property
    def SSH_REMOTE_HOST(self) -> Optional[str]:
        return self.ssh_remote_host

    @property
    def SSH_REMOTE_PORT(self) -> int:
        return self.ssh_remote_port

    @property
    def SSH_LOCAL_PORT(self) -> int:
        return self.ssh_local_port

    @property
    def DB_HOST(self) -> Optional[str]:
        return self.db_host

    @property
    def DB_PORT(self) -> Optional[int]:
        return int(self.db_port) if self.db_port else None

    @property
    def DB_USERNAME(self) -> Optional[str]:
        return self.db_username

    @property
    def DB_PASSWORD(self) -> Optional[str]:
        return self.db_password

    @property
    def DB_NAME(self) -> Optional[str]:
        return self.db_name

    @property
    def REDIS_HOST(self) -> Optional[str]:
        return self.redis_host

    @property
    def REDIS_PORT(self) -> Optional[int]:
        return self.redis_port

    @property
    def JWT_ACCESS_SECRET(self) -> Optional[str]:
        return self.jwt_access_secret

    @property
    def JWT_ACCESS_EXPIRATION_TIME(self) -> Optional[str]:
        return self.jwt_access_expiration_time

    @property
    def JWT_REFRESH_SECRET(self) -> Optional[str]:
        return self.jwt_refresh_secret

    @property
    def JWT_REFRESH_EXPIRATION_TIME(self) -> Optional[str]:
        return self.jwt_refresh_expiration_time

    @property
    def JWT_ADMIN_ACCESS_SECRET(self) -> Optional[str]:
        return self.jwt_admin_access_secret

    @property
    def JWT_ADMIN_ACCESS_EXPIRATION_TIME(self) -> Optional[str]:
        return self.jwt_admin_access_expiration_time

    @property
    def AWS_REGION(self) -> str:
        return self.aws_region

    @property
    def AWS_ACCESS_KEY_ID(self) -> Optional[str]:
        return self.aws_access_key_id

    @property
    def AWS_SECRET_ACCESS_KEY(self) -> Optional[str]:
        return self.aws_secret_access_key

    @property
    def AWS_S3_BUCKET_NAME(self) -> Optional[str]:
        return self.aws_s3_bucket_name

    @property
    def AWS_S3_CDN_URL(self) -> Optional[str]:
        return self.aws_s3_cdn_url

    @property
    def NODE_ENV(self) -> str:
        return self.environment

settings = Settings() 