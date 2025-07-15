from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.utils.date_handler import get_kst_now
from app.core.database.database_manager import Base


class BaseModel(Base):
    """기본 모델 클래스"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime(timezone=True), default=func.now(), comment="생성 시간")
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), comment="수정 시간"
    )
    deleted_at = Column(DateTime, nullable=True, comment="삭제 시간")