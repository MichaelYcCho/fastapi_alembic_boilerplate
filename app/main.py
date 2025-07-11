from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
from .api import api_router
from .core.database.database import Base, async_engine
from .core.errors import AppError
from .core.config import settings
from .core.database.database_manager import db_manager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="FastAPI 보일러플레이트",
    description="NestJS에서 FastAPI로 변환된 REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 예외 처리
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error_code": exc.error_code,
            "error_message": exc.error_message,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "error_code": exc.status_code,
            "error_message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": 500,
            "error_code": 500000,
            "error_message": "Internal Server Error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 헬스 체크 엔드포인트
@app.get("/health-check")
async def health_check():
    return {"status": "OK", "message": "Service is running"}

# 데이터베이스 상태 확인 엔드포인트
@app.get("/health-check/database")
async def database_health_check():
    return db_manager.health_check()

# 애플리케이션 시작 시 실행
@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI 애플리케이션이 시작됩니다.")
    
    # DatabaseManager 초기화
    if not db_manager.initialize_database():
        logger.error("데이터베이스 초기화에 실패했습니다.")
        return
    
    # 데이터베이스 테이블 생성 (개발 환경에서만)
    if settings.NODE_ENV == "dev":
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
# 애플리케이션 종료 시 실행
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI 애플리케이션이 종료됩니다.")
    # DatabaseManager 리소스 정리
    db_manager.cleanup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 