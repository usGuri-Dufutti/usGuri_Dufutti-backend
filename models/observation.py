from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.base import Base

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=False)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=False)
    phenophase_id = Column(Integer, nullable=False)
    observation_date = Column(Date, nullable=False)
    is_blooming = Column(Boolean, nullable=False)

    # relacionamento com Site
    site = relationship("Site", back_populates="observations")
    
    # relacionamento com Plant
    plant = relationship("Plant", back_populates="observations")
