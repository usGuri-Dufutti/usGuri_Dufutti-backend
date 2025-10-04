from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    
    # relacionamento com coordenadas do polígono
    coordinates = relationship("AreaCoordinate", back_populates="area", cascade="all, delete-orphan")
    
    # relacionamento com Plant (uma área tem várias plantas)
    plants = relationship("Plant", back_populates="area")


class AreaCoordinate(Base):
    __tablename__ = "area_coordinates"

    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    order = Column(Integer, nullable=False)  # para manter a ordem dos pontos do polígono
    
    # relacionamento com Area
    area = relationship("Area", back_populates="coordinates")
