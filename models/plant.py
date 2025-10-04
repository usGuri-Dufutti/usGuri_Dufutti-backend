from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=True)
    species = Column(String, nullable=False)

    # relacionamento com Observation (uma planta tem várias observações)
    observations = relationship("Observation", back_populates="plant")

    # relacionamento com Site (para acessar lat/long do local)
    site = relationship("Site", back_populates="plants")

    # relacionamento com Area (uma planta pode pertencer a uma área)
    area = relationship("Area", back_populates="plants")
