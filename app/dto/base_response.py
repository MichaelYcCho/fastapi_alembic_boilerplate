from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    message: str = Field(..., description="응답 메시지", example="success")
    
class BaseDataResponse(BaseModel, Generic[T]):
    data: T = Field(..., description="응답 데이터")
    
class BaseIdResponse(BaseModel):
    message: str = Field(..., description="성공 메시지", example="success")
    id: int = Field(..., description="생성된 엔티티 ID", example=1)
    
class ErrorResponse(BaseModel):
    status: int = Field(..., description="HTTP 상태 코드", example=400)
    error_code: int = Field(..., description="에러 코드", example=1001)
    error_message: str = Field(..., description="에러 메시지", example="Invalid input")
    timestamp: datetime = Field(..., description="에러 발생 시간")
    path: str = Field(..., description="요청 경로", example="/api/users")
    
class BasePaginatedResponse(BaseModel, Generic[T]):
    total: int = Field(..., description="전체 데이터 개수", example=100)
    page_number: int = Field(..., description="현재 페이지 번호", example=1)
    page_size: int = Field(..., description="페이지당 데이터 개수", example=10)
    data: list[T] = Field(..., description="페이지네이션된 데이터")
    
    @property
    def pages(self) -> int:
        """총 페이지 수 계산"""
        return (self.total + self.page_size - 1) // self.page_size 