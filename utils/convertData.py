import pandas as pd
from sqlalchemy import create_engine
from models.site import Site
from models.plant import Plant
from models.observation import Observation
from sqlalchemy.orm import Session
from utils.poligon import points_in_circle, generate_polygon
from models.area import Area, AreaCoordinate


# ⚡ Lê CSV
df = pd.read_csv("data/flores.csv")

# ⚡ Conexão com o banco
from core.config import settings
engine = create_engine(settings.db_url, echo=False)

# ----------------------
# 1️⃣ Sites únicos
# ----------------------
sites_df = df[["Site_ID", "Latitude", "Longitude", "Elevation_in_Meters"]].drop_duplicates()
sites_df = sites_df.rename(columns={
    "Site_ID": "id",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Elevation_in_Meters": "elevation"
})

# Remove duplicatas já existentes
existing_sites = pd.read_sql("SELECT id FROM sites", engine)["id"].tolist()
sites_df = sites_df[~sites_df["id"].isin(existing_sites)]

sites_df.to_sql("sites", engine, if_exists="append", index=False, method="multi")

# ----------------------
# 2️⃣ Plants únicos por Site e Species
# ----------------------
# ----------------------
# 2️⃣ Plants únicos por Site e Species (area_id nulo)
# ----------------------
plants_df = df[["Site_ID", "Species"]].drop_duplicates()
plants_df = plants_df.rename(columns={"Site_ID": "site_id", "Species": "species"})
plants_df["area_id"] = None  # vai ficar nulo por enquanto

# Remove duplicatas já existentes
existing_plants = pd.read_sql("SELECT site_id, species FROM plants", engine)
plants_df = plants_df.merge(existing_plants, on=["site_id", "species"], how="left", indicator=True)
plants_df = plants_df[plants_df["_merge"] == "left_only"].drop(columns="_merge")

plants_df.to_sql("plants", engine, if_exists="append", index=False, method="multi")
session = Session(engine)

# Pega todos os plants com latitude e longitude do site
plants_sql = pd.read_sql("""
SELECT p.id as plant_id, s.latitude, s.longitude, p.site_id
FROM plants p
JOIN sites s ON p.site_id = s.id
""", engine)
radius_m = 1000  # 1 km

# Agrupa por site (ou outro critério)
# Agrupa por site
for site_id, group in plants_sql.groupby("site_id"):
    points = list(zip(group["latitude"], group["longitude"]))

    # Se tiver 1 ou 2 plantas, cria "polígono" com os próprios pontos
    if len(points) < 3:
        polygon_coords = points
    else:
        polygon_coords = generate_polygon(points)

    if polygon_coords:
        new_area = Area()
        session.add(new_area)
        session.commit()
        session.refresh(new_area)

        for i, (lat, lon) in enumerate(polygon_coords):
            coord = AreaCoordinate(area_id=new_area.id, latitude=lat, longitude=lon, order=i)
            session.add(coord)
        session.commit()

        plant_ids = group["plant_id"].tolist()
        session.query(Plant).filter(Plant.id.in_(plant_ids))\
            .update({"area_id": new_area.id}, synchronize_session=False)
        session.commit()


# ----------------------
# 3️⃣ Observations
# ----------------------

df["Phenophase_Description"] = df["Phenophase_Description"].str.strip()

blooming_ids = [500, 501,502]
df["is_blooming"] = df["Phenophase_ID"].isin(blooming_ids)

observations_df = df.rename(columns={
    "Observation_ID": "id",
    "Site_ID": "site_id",
    "Species": "species",
    "Phenophase_ID": "phenophase_id",
    "Phenophase_Description": "description",  # aqui!
    "Observation_Date": "observation_date"
})[["id", "site_id", "species", "phenophase_id","description", "observation_date", "is_blooming"]]

# ⚡ Para associar Plant ID, cria mapeamento rápido

plants_mapping = pd.read_sql("SELECT id, site_id, species FROM plants", engine)
observations_df["species"] = observations_df["species"].str.strip().str.lower()

plants_mapping["species"] = plants_mapping["species"].str.strip().str.lower()

observations_df = observations_df.merge(plants_mapping, on=["site_id", "species"], how="left")
observations_df = observations_df.rename(columns={"id_y": "plant_id", "id_x": "id"})
observations_df = observations_df[["id", "site_id", "plant_id", "phenophase_id", "description", "observation_date", "is_blooming"]]

# Remove duplicatas já existentes
existing_obs = pd.read_sql("SELECT id FROM observations", engine)["id"].tolist()
observations_df = observations_df[~observations_df["id"].isin(existing_obs)]
missing_plants = observations_df[observations_df["plant_id"].isna()]

observations_df.to_sql("observations", engine, if_exists="append", index=False, method="multi")
