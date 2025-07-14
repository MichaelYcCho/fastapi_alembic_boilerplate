from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.models.base_model import BaseModel

class JwtStorage(BaseModel):
    __tablename__ = "jwt_storage"
    
    refresh_token = Column(String(255), nullable=True)
    refresh_token_expired_at = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="jwt_storage")