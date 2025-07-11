#!/usr/bin/env python3
"""
Alembic 마이그레이션 편의 스크립트

사용법:
  python scripts/migrate.py init              # 첫 마이그레이션 생성/적용 (SSH 터널링 사용)
  python scripts/migrate.py create "메시지"     # 새 마이그레이션 생성
  python scripts/migrate.py upgrade           # 마이그레이션 적용 (SSH 터널링 사용)
  python scripts/migrate.py downgrade         # 마이그레이션 롤백 (SSH 터널링 사용)
  python scripts/migrate.py current           # 현재 버전 확인
  python scripts/migrate.py history           # 마이그레이션 히스토리
  python scripts/migrate.py --no-ssh upgrade  # SSH 터널링 없이 업그레이드
"""

import sys
import subprocess
import argparse
from pathlib import Path
import os

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database.database_manager import db_manager
from app.core.config import settings


def run_alembic_command(command: list, use_ssh_tunnel: bool = True):
    """Alembic 명령어 실행"""

    # SSH 터널링 설정 (필요한 경우)
    if use_ssh_tunnel:
        print("🔧 SSH 터널링 설정 중...")
        if not db_manager.create_ssh_tunnel():
            print("❌ SSH 터널링 설정 실패")
            return False

    try:
        # Alembic 명령어 실행
        print(f"🚀 Alembic 명령어 실행: {' '.join(command)}")
        result = subprocess.run(command, cwd=project_root, check=True)

        if result.returncode == 0:
            print("✅ 명령어가 성공적으로 완료되었습니다!")
            return True
        else:
            print("❌ 명령어 실행에 실패했습니다.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ 명령어 실행 중 오류: {e}")
        return False
    finally:
        # SSH 터널 종료
        if use_ssh_tunnel:
            print("🔧 SSH 터널링 종료 중...")
            db_manager.close_ssh_tunnel()


def main():
    parser = argparse.ArgumentParser(description="Alembic 마이그레이션 편의 스크립트")
    parser.add_argument(
        "action",
        help="실행할 액션 (init, create, upgrade, downgrade, current, history)",
    )
    parser.add_argument(
        "message", nargs="?", help="create 액션에 사용할 마이그레이션 메시지"
    )
    parser.add_argument(
        "--no-ssh", action="store_true", help="SSH 터널링 강제 비활성화"
    )
    parser.add_argument(
        "--force-ssh", action="store_true", help="SSH 터널링 강제 활성화"
    )
    parser.add_argument("--debug", action="store_true", help="디버그 정보 출력")

    args = parser.parse_args()

    # 환경에 따른 SSH 터널링 사용 여부 결정
    environment = os.getenv("ENVIRONMENT", "local")

    if args.force_ssh:
        use_ssh_tunnel = True
        tunnel_reason = "강제 활성화"
    elif args.no_ssh:
        use_ssh_tunnel = False
        tunnel_reason = "강제 비활성화"
    else:
        use_ssh_tunnel = environment == "local"
        tunnel_reason = f"{environment} 환경 자동 설정"

    print(
        f"🔧 SSH 터널링: {'사용' if use_ssh_tunnel else '사용 안함'} ({tunnel_reason})"
    )

    # 디버그 정보 출력
    if args.debug:
        print("🔍 현재 설정 값들:")
        print(f"  ENVIRONMENT: {environment}")
        print(
            f"  DATABASE_URL: {'설정됨' if settings.database_url else '설정되지 않음'}"
        )
        print(f"  SSH_HOST: {settings.ssh_host or '설정되지 않음'}")
        print(f"  SSH_USER: {settings.ssh_user or '설정되지 않음'}")
        print(f"  SSH_KEY_PATH: {settings.ssh_key_path or '설정되지 않음'}")
        print(f"  SSH_REMOTE_HOST: {settings.ssh_remote_host or '설정되지 않음'}")
        print(f"  BASTION_HOST: {settings.bastion_host or '설정되지 않음'}")
        print(f"  BASTION_USERNAME: {settings.bastion_username or '설정되지 않음'}")
        print(f"  BASTION_KEY_FILE: {settings.bastion_key_file or '설정되지 않음'}")
        print()

    # 환경 변수 확인
    if not settings.database_url:
        print("❌ DATABASE_URL이 설정되지 않았습니다.")
        return 1

    if use_ssh_tunnel and not all(
        [settings.ssh_host, settings.ssh_user, settings.ssh_key_path]
    ):
        print("⚠️  SSH 터널링 설정이 불완전합니다.")
        if args.debug:
            missing = []
            if not settings.ssh_host:
                missing.append("SSH_HOST")
            if not settings.ssh_user:
                missing.append("SSH_USER")
            if not settings.ssh_key_path:
                missing.append("SSH_KEY_PATH")
            if not settings.ssh_remote_host:
                missing.append("SSH_REMOTE_HOST")
            print(f"   누락된 설정: {', '.join(missing)}")
        print("   --no-ssh 옵션을 사용하거나 SSH 설정을 완료하세요.")
        return 1

    success = False

    if args.action == "init":
        print("🎯 첫 마이그레이션 생성 및 적용")

        # 첫 마이그레이션 생성 (무조건 001)
        if run_alembic_command(
            [
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "Initial migration",
                "--rev-id",
                "001",
            ],
            use_ssh_tunnel,
        ):
            # 마이그레이션 적용
            success = run_alembic_command(
                ["alembic", "upgrade", "head"], use_ssh_tunnel
            )

    elif args.action == "create":
        if not args.message:
            print("❌ create 액션에는 마이그레이션 메시지가 필요합니다.")
            return 1

        print(f"🎯 새 마이그레이션 생성: {args.message}")

        # 순차적인 번호로 마이그레이션 생성
        def get_next_revision_number():
            """다음 순차적인 리비전 번호를 생성합니다."""
            versions_dir = project_root / "alembic" / "versions"
            if not versions_dir.exists():
                return "001"

            # 기존 마이그레이션 파일들의 번호를 추출
            existing_revisions = []
            for file in versions_dir.glob("*.py"):
                if file.name.startswith("__"):
                    continue
                # 파일명에서 번호 부분 추출 (예: 001, 002 등)
                import re

                match = re.match(r"^(\d+)_", file.name)
                if match:
                    existing_revisions.append(int(match.group(1)))

            if not existing_revisions:
                return "001"

            # 다음 번호 계산
            next_number = max(existing_revisions) + 1
            return f"{next_number:03d}"  # 3자리로 패딩

        next_rev = get_next_revision_number()
        print(f"📝 다음 리비전 번호: {next_rev}")

        success = run_alembic_command(
            [
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                args.message,
                "--rev-id",
                next_rev,
            ],
            use_ssh_tunnel,
        )

    elif args.action == "upgrade":
        print("🎯 마이그레이션 적용")
        success = run_alembic_command(["alembic", "upgrade", "head"], use_ssh_tunnel)

    elif args.action == "downgrade":
        print("🎯 마이그레이션 롤백")
        success = run_alembic_command(["alembic", "downgrade", "-1"], use_ssh_tunnel)

    elif args.action == "current":
        print("🎯 현재 마이그레이션 버전 확인")
        success = run_alembic_command(["alembic", "current"], use_ssh_tunnel)

    elif args.action == "history":
        print("🎯 마이그레이션 히스토리 확인")
        success = run_alembic_command(["alembic", "history"], use_ssh_tunnel)

    else:
        print(f"❌ 알 수 없는 액션: {args.action}")
        print("사용 가능한 액션: init, create, upgrade, downgrade, current, history")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
