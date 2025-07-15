from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from .config import settings
from typing import Optional, Dict, Any

# Password hashing context
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """비밀번호를 해시화합니다."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)

import re

def _parse_expiration_time(time_str: str) -> int:
    """환경변수에서 시간을 파싱합니다. (예: '11000000s' -> 11000000)"""
    if not time_str:
        return 3600
    
    # 숫자만 추출
    match = re.search(r'(\d+)', time_str)
    if match:
        return int(match.group(1))
    return 3600

def create_access_token(data: Dict[str, Any]) -> str:
    """액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    expiration_time = _parse_expiration_time(settings.JWT_ACCESS_EXPIRATION_TIME)
    expire = datetime.now(timezone.utc) + timedelta(seconds=expiration_time)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_ACCESS_SECRET, algorithm="HS256")
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """리프레시 토큰을 생성합니다."""
    to_encode = data.copy()
    expiration_time = _parse_expiration_time(settings.JWT_REFRESH_EXPIRATION_TIME)
    expire = datetime.now(timezone.utc) + timedelta(seconds=expiration_time)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str, secret_key: str) -> Optional[Dict[str, Any]]:
    """토큰을 검증하고 페이로드를 반환합니다."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None 