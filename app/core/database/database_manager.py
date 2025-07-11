import subprocess
import time
import logging
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """데이터베이스 연결 및 SSH 터널링 관리"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.ssh_tunnel_process = None
        self.ssh_tunnel_active = False

    def create_ssh_tunnel(self) -> bool:
        """SSH 터널링 생성"""
        try:
            if not all(
                [
                    settings.SSH_HOST,
                    settings.SSH_USER,
                    settings.SSH_KEY_PATH,
                    settings.SSH_REMOTE_HOST,
                ]
            ):
                logger.warning("SSH 터널링 설정이 완전하지 않습니다.")
                return False

            # 기존 터널 프로세스 종료
            self.close_ssh_tunnel()

            # SSH 터널링 명령어 구성
            ssh_command = [
                "ssh",
                "-i",
                settings.SSH_KEY_PATH,
                "-L",
                f"{settings.SSH_LOCAL_PORT}:{settings.SSH_REMOTE_HOST}:{settings.SSH_REMOTE_PORT}",
                f"{settings.SSH_USER}@{settings.SSH_HOST}",
                "-N",
            ]

            logger.info(f"SSH 터널링 시작: {settings.SSH_HOST}")

            # SSH 터널 프로세스 시작
            self.ssh_tunnel_process = subprocess.Popen(
                ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # 터널 연결 대기
            time.sleep(3)

            # 프로세스 상태 확인
            if self.ssh_tunnel_process.poll() is None:
                logger.info("SSH 터널링이 성공적으로 설정되었습니다.")
                self.ssh_tunnel_active = True
                return True
            else:
                logger.error("SSH 터널링 설정에 실패했습니다.")
                return False

        except Exception as e:
            logger.error(f"SSH 터널링 설정 중 오류: {e}")
            return False

    def close_ssh_tunnel(self):
        """SSH 터널 종료"""
        if self.ssh_tunnel_process:
            try:
                self.ssh_tunnel_process.terminate()
                self.ssh_tunnel_process.wait(timeout=5)
                logger.info("SSH 터널이 종료되었습니다.")
            except subprocess.TimeoutExpired:
                self.ssh_tunnel_process.kill()
                logger.warning("SSH 터널을 강제로 종료했습니다.")
            except Exception as e:
                logger.error(f"SSH 터널 종료 중 오류: {e}")
            finally:
                self.ssh_tunnel_process = None
                self.ssh_tunnel_active = False

    def initialize_database(self) -> bool:
        """데이터베이스 연결 초기화"""
        try:
            # IS_SSH 값에 따른 분기처리
            if settings.IS_SSH:
                logger.info("IS_SSH=true: SSH 터널링을 사용하여 데이터베이스에 연결합니다.")
                
                # SSH 터널링 시도
                if self.create_ssh_tunnel():
                    logger.info("SSH 터널링 성공, 터널을 통해 데이터베이스에 연결합니다.")
                    database_url = self._get_tunneled_database_url()
                else:
                    logger.warning("SSH 터널링 실패, 직접 연결을 시도합니다.")
                    database_url = settings.DATABASE_URL
            else:
                logger.info("IS_SSH=false: 직접 데이터베이스에 연결합니다.")
                database_url = settings.DATABASE_URL

            if not database_url:
                logger.error("데이터베이스 URL이 설정되지 않았습니다.")
                return False

            # 데이터베이스 엔진 생성
            self.engine = create_engine(
                database_url, pool_pre_ping=True, pool_recycle=300
            )

            # 세션 팩토리 생성
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )

            # 연결 테스트
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            connection_type = "SSH 터널" if self.ssh_tunnel_active else "직접 연결"
            logger.info(f"데이터베이스 연결이 성공적으로 설정되었습니다. (연결 방식: {connection_type})")
            return True

        except Exception as e:
            logger.error(f"데이터베이스 초기화 중 오류: {e}")
            return False

    def _get_tunneled_database_url(self) -> str:
        """SSH 터널링을 통한 데이터베이스 URL 생성"""
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL이 설정되지 않았습니다.")
        
        # postgresql://user:pass@host:port/db -> postgresql://user:pass@localhost:2/db
        tunneled_url = re.sub(
            r"@[^:]+:\d+", f"@localhost:{settings.SSH_LOCAL_PORT}", settings.DATABASE_URL
        )
        logger.info(f"터널링된 데이터베이스 URL: {tunneled_url}")
        return tunneled_url

    def get_db_session(self):
        """데이터베이스 세션 생성"""
        if not self.SessionLocal:
            raise Exception("데이터베이스가 초기화되지 않았습니다.")

        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def health_check(self) -> dict:
        """데이터베이스 상태 확인"""
        try:
            if not self.engine:
                return {
                    "status": "disconnected",
                    "message": "데이터베이스가 초기화되지 않았습니다.",
                }

            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            connection_type = "SSH 터널" if self.ssh_tunnel_active else "직접 연결"
            return {
                "status": "connected", 
                "message": f"데이터베이스 연결이 정상입니다. (연결 방식: {connection_type})",
                "connection_type": connection_type,
                "ssh_tunnel_active": self.ssh_tunnel_active
            }

        except Exception as e:
            return {"status": "error", "message": f"데이터베이스 연결 오류: {str(e)}"}

    def cleanup(self):
        """리소스 정리"""
        self.close_ssh_tunnel()


# 전역 데이터베이스 매니저 인스턴스
db_manager = DatabaseManager() 