"""
Main entry point for the wind turbine hub height project.

Takes a coordinate, validates it, calculates the wind profile across
the configured height range, and saves/displays the results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from coordinates import validate_coordinate, CoordinateOutOfBoundsError
from wind_profile import calculate_wind_profile
from visualization import (
    _get_output_paths,
    print_profile_table,
    save_profile_csv,
    save_summary,
    plot_profile,
    create_report,
)


def run(lat: float, lon: float) -> None:
    """
    Runs the full pipeline for a single coordinate: validate, load
    wind data, calculate the profile, and save/display the results.
    """
    print(f"Validating coordinate ({lat}, {lon}) ...")
    coord = validate_coordinate(lat, lon)
    print(f"Coordinate is valid: {coord}\n")

    print("Calculating wind profile (this may take a while - loading HOSTRADA data) ...")
    profile, v_ref, alpha, clc_code = calculate_wind_profile(coord)

    print_profile_table(profile)

    paths = _get_output_paths(coord)
    save_profile_csv(profile, paths["csv"])
    save_summary(coord, v_ref, paths["summary"])
    plot_profile(profile, coord, save_path=paths["png"])

    report_path = paths["csv"].parent / "report.pdf"
    create_report(profile, coord, v_ref, alpha, clc_code, report_path)

    print(f"\nDone. Results saved in: {paths['csv'].parent}")


if __name__ == "__main__":
    #Enter your coordinates here ! Use the same form as given in the example below 
    LAT = 50.08512
    LON = 8.688460

    try:
        run(LAT, LON)
    except CoordinateOutOfBoundsError as e:
        print(f"Invalid coordinate: {e}")
    except FileNotFoundError as e:
        print(f"Missing data: {e}")