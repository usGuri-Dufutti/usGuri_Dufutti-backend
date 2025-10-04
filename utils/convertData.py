import pandas as pd
from sqlalchemy import create_engine
from models.site import Site
from models.plant import Plant
from models.observation import Observation

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
plants_df = df[["Site_ID", "Species"]].drop_duplicates()
plants_df = plants_df.rename(columns={"Site_ID": "site_id", "Species": "species"})

# Remove duplicatas já existentes
existing_plants = pd.read_sql("SELECT site_id, species FROM plants", engine)
plants_df = plants_df.merge(existing_plants, on=["site_id", "species"], how="left", indicator=True)
plants_df = plants_df[plants_df["_merge"] == "left_only"].drop(columns="_merge")

plants_df.to_sql("plants", engine, if_exists="append", index=False, method="multi")

# ----------------------
# 3️⃣ Observations
# ----------------------
blooming_ids = [500, 501]
df["is_blooming"] = df["Phenophase_ID"].isin(blooming_ids)

observations_df = df.rename(columns={
    "Observation_ID": "id",
    "Site_ID": "site_id",
    "Species": "species",
    "Phenophase_ID": "phenophase_id",
    "Observation_Date": "observation_date"
})[["id", "site_id", "species", "phenophase_id", "observation_date", "is_blooming"]]

# ⚡ Para associar Plant ID, cria mapeamento rápido
plants_mapping = pd.read_sql("SELECT id, site_id, species FROM plants", engine)
observations_df = observations_df.merge(plants_mapping, on=["site_id", "species"], how="left")
observations_df = observations_df.rename(columns={"id_y": "plant_id", "id_x": "id"})
observations_df = observations_df[["id", "site_id", "plant_id", "phenophase_id", "observation_date", "is_blooming"]]

# Remove duplicatas já existentes
existing_obs = pd.read_sql("SELECT id FROM observations", engine)["id"].tolist()
observations_df = observations_df[~observations_df["id"].isin(existing_obs)]

observations_df.to_sql("observations", engine, if_exists="append", index=False, method="multi")
