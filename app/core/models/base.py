from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

from app.utils.date_handler import get_kst_now


Base = declarative_base()

class BaseModel(Base):
    """기본 모델 클래스"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    created_at = Column(DateTime, default=get_kst_now, comment="생성 시간")
    updated_at = Column(
        DateTime, default=get_kst_now, onupdate=get_kst_now, comment="수정 시간"
    )
    deleted_at = Column(DateTime, nullable=True, comment="삭제 시간")