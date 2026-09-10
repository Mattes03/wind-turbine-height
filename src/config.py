"""
Project-wide configuration: centralised file paths, constants and lookup tables.
"""

from pathlib import Path

# --- Paths -------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"

#first checkup if the entered coordinates could be in Germany  
GERMANY_BBOX = {
    "lat_min": 47.2,
    "lat_max": 55.1,
    "lon_min": 5.8,
    "lon_max": 15.1,
}

#exact border of Germany, to cofirm that the coordinates are within the country 
GERMANY_BORDER_PATH = DATA_RAW / "ShapeGermany" / "Germany.shp"

#Data path for LBM files
LBM_PATH = DATA_RAW / "LBM" / "LBMDE.gpkg"

#inspecting HOSTRADA wind files 
HOSTRADA_WIND_TEST_FILE = DATA_RAW / "hostrada" / "sfcWind_1hr_HOSTRADA-v1-0_BE_gn_2023010100-2023013123.nc"

# --- HOSTRADA settings ---------------------------------------------------
HOSTRADA_REFERENCE_HEIGHT_M = 10  # HOSTRADA only provides wind speed at 10 m
HOSTRADA_YEARS = list(range(2016, 2026))  # 10-year window
# HOSTRADA_YEARS = [2025] #only one year range for windspeed calculations, for testing purpuses 
# --- Wind profile calculation settings ----------------------------------
HEIGHT_RANGE_M = range(50, 210, 10)  # heights to evaluate, 50-200 m in 10 m steps



# --- CLC code -> roughness length z0 lookup table -------------------------
# Source: Silva et al., "roughness length classification of Corine land
# cover classes" - values are z0 in metres.
CLC_Z0_LOOKUP = {
    111: 1.2,
    311: 0.75, 312: 0.75, 313: 0.75,
    141: 0.6, 324: 0.6, 334: 0.6,
    112: 0.5, 121: 0.5, 123: 0.5, 133: 0.5, 142: 0.5,
    242: 0.3, 243: 0.3, 244: 0.3,
    221: 0.1, 222: 0.1, 223: 0.1, 241: 0.1,
    122: 0.075,
    211: 0.05, 212: 0.05, 213: 0.05, 411: 0.05, 421: 0.05,
    231: 0.03, 321: 0.03, 322: 0.03, 323: 0.03,
    124: 0.005, 131: 0.005, 132: 0.005, 332: 0.005, 333: 0.005,
    335: 0.001,
    412: 0.0005, 422: 0.0005, 423: 0.0005,
    331: 0.0003,
    511: 0.0001, 512: 0.0001, 521: 0.0001, 522: 0.0001, 523: 0.0001,
}
DEFAULT_Z0 = 0.05  # fallback if CLC code not found



if __name__ == "__main__":
    # quick manual check when running this file directly
    print("PROJECT_ROOT:", PROJECT_ROOT)
    print("DATA_RAW exists:", DATA_RAW.exists())
    print("DATA_PROCESSED exists:", DATA_PROCESSED.exists())
    print("Number of CLC codes in lookup:", len(CLC_Z0_LOOKUP))


CLC_CLASS_NAMES = {
    111: "Durchgängig städtische Prägung",
    112: "Nicht durchgängig städtische Prägung",
    121: "Industrie- und Gewerbeflächen",
    122: "Straßen-, Eisenbahnnetze und zugeordnete Flächen",
    123: "Hafengebiete",
    133: "Baustellen",
    141: "Städtische Grünflächen",
    142: "Sport- und Freizeitanlagen",
    211: "Nicht bewässertes Ackerland",
    221: "Weinbauflächen",
    222: "Obst- und Beerenobstbestände",
    223: "Olivenhaine",
    231: "Wiesen und Weiden",
    241: "Einjährige Kulturen in Verbindung mit Dauerkulturen",
    242: "Komplexe Parzellenstrukturen",
    243: "Landwirtschaftlich genutztes Land mit natürlicher Bodenbedeckung",
    244: "Land- und forstwirtschaftliche Flächen",
    311: "Laubwälder",
    312: "Nadelwälder",
    313: "Mischwälder",
    321: "Natürliches Grünland",
    322: "Heiden und Moorheiden",
    324: "Wald-Strauch-Übergangsstadien",
    331: "Strände, Dünen und Sandflächen",
    332: "Felsflächen ohne Vegetation",
    333: "Flächen mit spärlicher Vegetation",
    334: "Brandflächen",
    411: "Sümpfe",
    412: "Torfmoore",
    421: "Salzwiesen",
    422: "Salinen",
    423: "In der Gezeitenzone liegende Flächen",
    511: "Gewässerläufe",
    512: "Wasserflächen",
    521: "Lagunen",
    522: "Mündungsgebiete",
    523: "Meere und Ozeane",
}
DEFAULT_CLASS_NAME = "Unbekannte Klasse (Fallback-Wert verwendet)"




