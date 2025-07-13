from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.models.base import BaseModel

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STAFF = "STAFF"
    COMMON = "COMMON"

class User(BaseModel):
    """사용자 모델"""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_email', 'email', unique=True),
    )
    
    email = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    profile_name = Column(String(30), nullable=False)
    role = Column(String(20), default=UserRole.COMMON, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    jwt_storage = relationship("JwtStorage", back_populates="user", uselist=False) 