from sqlalchemy import Column, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.base import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True,index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Integer, nullable=False)

    observations = relationship(
        "Observation",
        back_populates="site",
        cascade="all, delete-orphan"
    )