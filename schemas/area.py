from pydantic import BaseModel
from typing import List, Optional
from datetime import date


# Schemas para Observation
class ObservationBase(BaseModel):
    phenophase_id: int
    observation_date: date
    is_blooming: bool

class ObservationResponse(ObservationBase):
    id: int
    site_id: int
    plant_id: int
    description: str

    class Config:
        orm_mode = True


# Schemas para Site
class SiteBase(BaseModel):
    latitude: float
    longitude: float
    elevation: int

class SiteResponse(SiteBase):
    id: int

    class Config:
        orm_mode = True


# Schemas para Plant
class PlantBase(BaseModel):
    species: str

class PlantWithObservations(PlantBase):
    id: int
    site_id: int
    area_id: Optional[int]
    site: SiteResponse
    observations: List[ObservationResponse]

    class Config:
        orm_mode = True


# Schemas para AreaCoordinate
class AreaCoordinateBase(BaseModel):
    latitude: float
    longitude: float
    order: int

class AreaCoordinateResponse(AreaCoordinateBase):
    id: int

    class Config:
        orm_mode = True
        extra = "ignore"



# Schemas para Area
class AreaCreate(BaseModel):
    coordinates: List[AreaCoordinateBase]

class AreaResponse(BaseModel):
    id: int
    description: Optional[str] = None
    coordinates: List[AreaCoordinateResponse]
    plants: List[PlantWithObservations]

    class Config:
        orm_mode = True



class AreaListResponse(BaseModel):
    id: int
    coordinates: List[AreaCoordinateResponse]
    description: Optional[str] = None

    class Config:
        orm_mode = True
        extra = "ignore"
