"""
Calculates wind speed at multiple hub heights using the power law:

    v(h) = v_ref * (h / h_ref) ** alpha

Combines the reference wind speed (from hostrada_prep.py) and the
shear exponent alpha (from alpha_calculation.py) into a wind profile
across the configured height range (HEIGHT_RANGE_M in config.py).
"""

from config import HEIGHT_RANGE_M, HOSTRADA_REFERENCE_HEIGHT_M
from coordinates import Coordinate
from hostrada_prep import get_reference_wind_speed
from alpha_calculation import get_alpha_for_coordinate


def calculate_wind_speed_at_height(
    v_ref: float, alpha: float, height: float, h_ref: float = HOSTRADA_REFERENCE_HEIGHT_M
) -> float:
    """
    Returns the wind speed at a given height, using the power law:
    v(h) = v_ref * (h / h_ref) ** alpha
    """
    return v_ref * (height / h_ref) ** alpha


def calculate_wind_profile(coord: Coordinate) -> tuple:
    v_ref = get_reference_wind_speed(coord)
    alpha, clc_code = get_alpha_for_coordinate(coord)

    profile = {}
    for height in HEIGHT_RANGE_M:
        profile[height] = calculate_wind_speed_at_height(v_ref, alpha, height)

    return profile, v_ref, alpha, clc_code


if __name__ == "__main__":
    test_coord = Coordinate(lat=52.5200, lon=13.4050)  # Berlin

    print(f"Calculating wind profile for {test_coord} ...")
    profile, v_ref = calculate_wind_profile(test_coord)

    print(f"\nv_ref: {v_ref:.3f} m/s")
    print("\nHeight (m) | Wind speed (m/s)")
    print("-" * 32)
    for height, speed in profile.items():
        print(f"{height:>10} | {speed:.3f}")