from logging.config import fileConfig
import os
import sys
from pathlib import Path
import re

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.database import Base
from app.core.config import settings
from app.core.database.database_manager import db_manager

# 모델들을 명시적으로 import (Alembic이 테이블을 인식하도록)
from app.users.models.user import User
from app.auth.models.jwt_storage import JwtStorage

# IDE의 자동 import 정리를 방지하기 위해 명시적으로 사용
__all__ = ["User", "JwtStorage"]

# Alembic이 모델을 인식할 수 있도록 메타데이터에 등록
# (이렇게 하면 IDE가 import를 삭제하지 않음)
_models = [User, JwtStorage]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config  # type: ignore

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# SSH 터널링 설정 플래그 - 환경에 따라 자동 결정
environment = os.getenv("ENVIRONMENT", "local")
USE_SSH_TUNNEL_ENV = os.getenv("USE_SSH_TUNNEL", "auto").lower()

if USE_SSH_TUNNEL_ENV == "auto":
    USE_SSH_TUNNEL = environment == "local"
elif USE_SSH_TUNNEL_ENV in ["true", "1", "yes"]:
    USE_SSH_TUNNEL = True
else:
    USE_SSH_TUNNEL = False

print(
    f"🔧 SSH 터널링: {'사용' if USE_SSH_TUNNEL else '사용 안함'} ({environment} 환경)"
)


def get_next_revision_number():
    """다음 순차적인 리비전 번호를 생성합니다."""
    versions_dir = Path(__file__).parent / "versions"
    if not versions_dir.exists():
        return "001"

    # 기존 마이그레이션 파일들의 번호를 추출
    existing_revisions = []
    for file in versions_dir.glob("*.py"):
        if file.name.startswith("__"):
            continue
        # 파일명에서 번호 부분 추출 (예: 001, 002 등)
        match = re.match(r"^(\d+)_", file.name)
        if match:
            existing_revisions.append(int(match.group(1)))

    if not existing_revisions:
        return "001"

    # 다음 번호 계산
    next_number = max(existing_revisions) + 1
    return f"{next_number:03d}"  # 3자리로 패딩


def get_database_url():
    """환경 변수에서 데이터베이스 URL을 가져와서 동적으로 설정"""
    db_url = settings.DATABASE_URL

    if not db_url:
        raise ValueError("DATABASE_URL이 설정되지 않았습니다.")

    # SSH 터널링 사용 시 localhost로 변경
    if USE_SSH_TUNNEL and all(
        [settings.SSH_HOST, settings.SSH_USER, settings.SSH_KEY_PATH]
    ):
        # postgresql://user:pass@host:port/db -> postgresql://user:pass@localhost:5432/db
        modified_url = re.sub(
            r"@[^:]+:\d+", f"@localhost:{settings.SSH_LOCAL_PORT}", db_url
        )
        return modified_url

    return db_url


def setup_ssh_tunnel():
    """SSH 터널링 설정"""
    if USE_SSH_TUNNEL and all(
        [settings.SSH_HOST, settings.SSH_USER, settings.SSH_KEY_PATH]
    ):
        print("🔧 SSH 터널링 설정 중...")
        if db_manager.create_ssh_tunnel():
            print("✅ SSH 터널링이 성공적으로 설정되었습니다.")
            return True
        else:
            print("❌ SSH 터널링 설정에 실패했습니다.")
            return False
    return True


def cleanup_ssh_tunnel():
    """SSH 터널링 정리"""
    if USE_SSH_TUNNEL:
        print("🔧 SSH 터널링 종료 중...")
        db_manager.close_ssh_tunnel()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # SSH 터널링 설정
    tunnel_success = setup_ssh_tunnel()
    if not tunnel_success:
        raise RuntimeError("SSH 터널링 설정에 실패했습니다.")

    try:
        # 데이터베이스 URL 설정
        database_url = get_database_url()

        # Alembic 설정 오버라이드
        configuration = config.get_section(config.config_ini_section)
        configuration["sqlalchemy.url"] = database_url

        print("데이터 베이스 연결중")
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

    finally:
        # SSH 터널링 정리
        cleanup_ssh_tunnel()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 