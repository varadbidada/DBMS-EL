from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Location(Base):
    __tablename__ = "location"
    __table_args__ = (UniqueConstraint("city", "state", "country", "zip_code"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    zip_code = Column(String(20))

    # relationships (optional backrefs)
    users = relationship("User", back_populates="location", cascade="all, delete-orphan")
    donors = relationship("Donor", back_populates="location", cascade="all, delete-orphan")
    banks = relationship("BloodBank", back_populates="location", cascade="all, delete-orphan")
    hospitals = relationship("Hospital", back_populates="location", cascade="all, delete-orphan")
