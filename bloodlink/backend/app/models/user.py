from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, UniqueConstraint, CheckConstraint, Numeric, Text, Index
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("username"),
        UniqueConstraint("email"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    location_id = Column(Integer, ForeignKey("location.id", ondelete="SET NULL", onupdate="CASCADE"))
    location = relationship("Location", back_populates="users")
