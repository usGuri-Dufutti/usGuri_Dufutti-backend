from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    species = Column(String, nullable=False)
    
    # relacionamento com Observation (uma planta tem várias observações)
    observations = relationship("Observation", back_populates="plant", cascade="all, delete-orphan")
