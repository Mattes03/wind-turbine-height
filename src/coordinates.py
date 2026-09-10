"""
Handles the user-provided coordinate: validates it and packages it
into a simple structure the rest of the pipeline can use.
"""

from dataclasses import dataclass

import geopandas as gpd
from shapely.geometry import Point

from config import GERMANY_BBOX, GERMANY_BORDER_PATH


@dataclass
class Coordinate:
    lat: float
    lon: float


class CoordinateOutOfBoundsError(ValueError):
    """Raised when a coordinate falls outside Germany's border."""
    pass


# Load once at import time, not on every function call.
# The downloaded file contains all world countries despite its filename,
# so it's filtered down to Germany's row specifically.
_world_borders = gpd.read_file(GERMANY_BORDER_PATH)
_germany_border = _world_borders[_world_borders["SOVEREIGNT"] == "Germany"]


def validate_coordinate(lat: float, lon: float) -> Coordinate:
    if not (-90 <= lat <= 90):
        raise ValueError(f"Latitude {lat} is not a valid latitude (-90 to 90).")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Longitude {lon} is not a valid longitude (-180 to 180).")

    if not (GERMANY_BBOX["lat_min"] <= lat <= GERMANY_BBOX["lat_max"]) or not (
        GERMANY_BBOX["lon_min"] <= lon <= GERMANY_BBOX["lon_max"]
    ):
        raise CoordinateOutOfBoundsError(
            f"Coordinate ({lat}, {lon}) is outside Germany's bounding box."
        )

    point = Point(lon, lat)
    is_inside = _germany_border.contains(point).any()

    if not is_inside:
        raise CoordinateOutOfBoundsError(
            f"Coordinate ({lat}, {lon}) is inside the bounding box but "
            f"outside Germany's actual border."
        )

    return Coordinate(lat=lat, lon=lon)


if __name__ == "__main__":
    test_cases = [
        (52.5200, 13.4050, "Berlin - should pass"),
        (53.5511, 9.9937, "Hamburg - should pass"),
        (48.1351, 11.5820, "Munich - should pass"),
        (40.7128, -74.0060, "New York - should fail (out of bbox)"),
        (47.5, 7.0, "Basel/Switzerland border area - should fail (in bbox, outside border)"),
        (999, 13.4, "Invalid latitude - should fail (ValueError)"),
    ]

    for lat, lon, description in test_cases:
        try:
            coord = validate_coordinate(lat, lon)
            print(f"OK   | {description} -> {coord}")
        except (ValueError, CoordinateOutOfBoundsError) as e:
            print(f"FAIL | {description} -> {e}")