from fastapi import HTTPException
from typing import Dict, Any

class AppError(HTTPException):
    """애플리케이션 커스텀 에러 클래스"""
    
    def __init__(self, error_info: Dict[str, Any]):
        self.error_code = error_info.get("errorCode", 500000)
        self.error_message = error_info.get("message", "Internal Server Error")
        self.status_code = error_info.get("status", 500)
        
        super().__init__(
            status_code=self.status_code,
            detail={
                "error_code": self.error_code,
                "error_message": self.error_message
            }
        )

# 인증 관련 에러들
AUTH_ERRORS = {
    "NOT_EXIST_JWT_STORAGE": {
        "errorCode": 200001,
        "message": "JWT 저장소가 존재하지 않습니다",
        "status": 400
    },
    "INVALID_ACCESS_TOKEN": {
        "errorCode": 200002,
        "message": "유효하지 않은 액세스 토큰입니다",
        "status": 401
    },
    "INVALID_REFRESH_TOKEN": {
        "errorCode": 200003,
        "message": "유효하지 않은 리프레시 토큰입니다",
        "status": 401
    },
    "EXPIRED_TOKEN": {
        "errorCode": 200004,
        "message": "토큰이 만료되었습니다",
        "status": 401
    },
    "INVALID_SIGNATURE": {
        "errorCode": 200005,
        "message": "유효하지 않은 서명입니다",
        "status": 401
    },
    "FAILED_AUTHENTICATE": {
        "errorCode": 200006,
        "message": "인증에 실패했습니다",
        "status": 401
    },
    "MISSING_AUTHORIZATION_HEADER": {
        "errorCode": 200007,
        "message": "Authorization 헤더가 누락되었습니다",
        "status": 401
    },
    "MISSING_JWT_TOKEN": {
        "errorCode": 200008,
        "message": "JWT 토큰이 누락되었습니다",
        "status": 401
    },
}

# 사용자 관련 에러들
USERS_ERRORS = {
    "NOT_EXIST_USER": {
        "errorCode": 100001,
        "status": 400,
        "message": "사용자를 찾을 수 없습니다",
    },
    "USER_EMAIL_ALREADY_EXIST": {
        "errorCode": 100002,
        "status": 400,
        "message": "이미 존재하는 이메일입니다",
    },
    "FAILED_CREATE_USER": {
        "errorCode": 100003,
        "status": 400,
        "message": "사용자 생성에 실패했습니다",
    },
    "FAILED_GET_USER_PROFILE": {
        "errorCode": 100004,
        "status": 400,
        "message": "사용자 프로필 조회에 실패했습니다",
    },
    "FAILED_UPDATE_USER": {
        "errorCode": 100005,
        "status": 400,
        "message": "사용자 업데이트에 실패했습니다",
    },
    "FAILED_DELETE_USER": {
        "errorCode": 100006,
        "status": 400,
        "message": "사용자 삭제에 실패했습니다",
    },
} 