from sqlalchemy import Column, Integer, Date, ForeignKey,Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from db.base import Base

class Observation(Base):
    __tablename__ = "observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    phenophase_id = Column(Integer, nullable=False)
    observation_date = Column(Date, nullable=False)
    is_blooming = Column(Boolean, nullable=False)

    # relacionamento com Site
    site = relationship("Site", back_populates="observations")
