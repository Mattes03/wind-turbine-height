"""
Loads the LBM-DE2021 land cover dataset and extracts the CLC21 land
cover code for the polygon containing a given coordinate.

This CLC code is later used (in alpha_calculation.py) to look up a
roughness length z0 via CLC_Z0_LOOKUP in config.py.

The LBM-DE2021 file is ~5.9 GB, so this module never loads the full
dataset into memory - it uses a small bounding-box filter around the
target coordinate to only read nearby polygons.
"""

import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point

from config import LBM_PATH
from coordinates import Coordinate

LBM_LAYER = "LBMDE_2021"
LBM_CRS = "EPSG:25832"  # UTM Zone 32N (ETRS89), confirmed from the file's metadata

# Half-width of the bounding box (in metres) used to filter the file
# read around the target point. LBM-DE's minimum mapping unit is 1 ha
# (100m x 100m), so 500m gives comfortable margin to guarantee the
# containing polygon is included, without reading unnecessary area.
BBOX_BUFFER_M = 500

# Reused across calls rather than rebuilt each time - building a
# Transformer has a small one-time setup cost.
_transformer = Transformer.from_crs("EPSG:4326", LBM_CRS, always_xy=True)


def _coordinate_to_utm(coord: Coordinate) -> Point:
    """
    Converts a WGS84 (lat/lon) Coordinate into a shapely Point in the
    LBM-DE dataset's CRS (EPSG:25832 / UTM Zone 32N).
    """
    x, y = _transformer.transform(coord.lon, coord.lat)
    return Point(x, y)


def get_clc_code(coord: Coordinate) -> int:
    """
    Returns the CLC21 land cover code for the LBM-DE polygon that
    contains the given coordinate.

    Raises a ValueError if no polygon is found at that location
    (should not normally happen for a coordinate already validated
    to be inside Germany, but guarded against regardless).
    """
    point = _coordinate_to_utm(coord)

    bbox = (
        point.x - BBOX_BUFFER_M,
        point.y - BBOX_BUFFER_M,
        point.x + BBOX_BUFFER_M,
        point.y + BBOX_BUFFER_M,
    )

    # bbox= filters at the file level, so only polygons near the point
    # are actually read - the full 5.9GB file is never loaded at once.
    gdf = gpd.read_file(LBM_PATH, layer=LBM_LAYER, bbox=bbox)

    if gdf.empty:
        raise ValueError(
            f"No LBM-DE polygons found near coordinate {coord} "
            f"(bbox={bbox}). Coordinate may be outside the dataset's coverage."
        )

    match = gdf[gdf.contains(point)]

    if match.empty:
        raise ValueError(
            f"Found {len(gdf)} nearby polygons, but none contain "
            f"coordinate {coord} exactly. This may indicate a coordinate "
            f"very close to a polygon boundary or a data gap."
        )

    return int(match.iloc[0]["CLC21"])


if __name__ == "__main__":
    test_coord = Coordinate(lat=48.9989, lon=13.4014)  # Großer Rachel, Nationalpark Bayerischer Wald

    print(f"Looking up CLC code for {test_coord} ...")
    clc_code = get_clc_code(test_coord)
    print(f"CLC21 code: {clc_code}")