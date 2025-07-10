from pydantic import BaseModel
from typing import Optional, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class BaseResponse(BaseModel):
    message: str
    
class ErrorResponse(BaseModel):
    status: int
    error_code: int
    error_message: str
    timestamp: datetime
    path: str
    
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int 