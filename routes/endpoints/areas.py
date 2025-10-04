from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from db.session import SessionLocal
from models.area import Area, AreaCoordinate
from models.plant import Plant
from schemas.area import AreaCreate, AreaResponse, AreaListResponse

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
def create_area(area_data: AreaCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova área com suas coordenadas (polígono)
    """
    # Criar a área
    new_area = Area()
    db.add(new_area)
    db.flush()  # Para obter o ID
    
    # Adicionar coordenadas
    for coord_data in area_data.coordinates:
        coordinate = AreaCoordinate(
            area_id=new_area.id,
            latitude=coord_data.latitude,
            longitude=coord_data.longitude,
            order=coord_data.order
        )
        db.add(coordinate)
    
    db.commit()
    db.refresh(new_area)
    
    # Carregar com relacionamentos
    area = db.query(Area).options(
        joinedload(Area.coordinates),
        joinedload(Area.plants)
            .joinedload(Plant.site),
        joinedload(Area.plants)
            .joinedload(Plant.observations)
    ).filter(Area.id == new_area.id).first()
    
    return area


@router.get("/", response_model=List[AreaListResponse])
def list_areas(db: Session = Depends(get_db)):
    """
    Lista todas as áreas (sem incluir plantas - para performance)
    """
    areas = db.query(Area).options(
        joinedload(Area.coordinates)
    ).all()
    
    return areas


@router.get("/{area_id}", response_model=AreaResponse)
def get_area(area_id: int, db: Session = Depends(get_db)):
    """
    Retorna uma área específica com TODOS os dados relacionados:
    - Coordenadas do polígono
    - Plantas da área
    - Site de cada planta (lat/long)
    - Observações de cada planta
    """
    area = db.query(Area).options(
        joinedload(Area.coordinates),
        joinedload(Area.plants)
            .joinedload(Plant.site),
        joinedload(Area.plants)
            .joinedload(Plant.observations)
    ).filter(Area.id == area_id).first()
    
    if not area:
        raise HTTPException(status_code=404, detail="Área não encontrada")
    
    return area


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_area(area_id: int, db: Session = Depends(get_db)):
    """
    Deleta uma área (as coordenadas são deletadas automaticamente por cascade)
    """
    area = db.query(Area).filter(Area.id == area_id).first()
    
    if not area:
        raise HTTPException(status_code=404, detail="Área não encontrada")
    
    # Remove area_id das plantas antes de deletar
    db.query(Plant).filter(Plant.area_id == area_id).update({"area_id": None})
    
    db.delete(area)
    db.commit()
    
    return None
