from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.poligon import generate_polygon, points_in_circle
from models.area import Area, AreaCoordinate
from models.plant import Plant
from models.site import Site
from models.observation import Observation
from core.config import settings

# Conexão
engine = create_engine(settings.db_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

with SessionLocal() as session:
    # Pega alguns plants de teste
    plants = session.query(Plant).limit(5).all()
    points = [(p.latitude, p.longitude) for p in plants if hasattr(p, "latitude") and hasattr(p, "longitude")]

    if 3 <= len(points) <= 8:
        polygon_coords = generate_polygon(points)
        if polygon_coords:
            # Cria nova Area
            new_area = Area()
            session.add(new_area)
            session.flush()  # para garantir que new_area.id existe

            # Cria AreaCoordinates
            for i, (lat, lon) in enumerate(polygon_coords):
                coord = AreaCoordinate(area_id=new_area.id, latitude=lat, longitude=lon, order=i)
                session.add(coord)

            # Atualiza plants
            plant_ids = [p.id for p in plants]
            session.query(Plant).filter(Plant.id.in_(plant_ids)).update({"area_id": new_area.id}, synchronize_session=False)

            session.commit()
            print(f"✅ Área {new_area.id} criada com {len(plant_ids)} plants e {len(polygon_coords)} coordenadas")
        else:
            print("⚠️ Não foi possível gerar polígono")
    else:
        print("⚠️ Número de pontos insuficiente ou maior que 8")
