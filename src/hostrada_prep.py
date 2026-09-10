"""
Loads HOSTRADA wind speed data for the configured year range and
extracts the near-surface wind speed time series at the grid cell
nearest to a given coordinate.

Also provides the 10-year mean reference wind speed (v_ref) used later
as the starting point for the power law extrapolation - this was
originally planned as a separate "annual mean" module, but folded in
here since it's a direct, small continuation of the extraction step.
"""

import numpy as np
import xarray as xr

from config import DATA_RAW, HOSTRADA_YEARS
from coordinates import Coordinate

HOSTRADA_DIR = DATA_RAW / "hostrada"


def _get_file_paths() -> list:
    """
    Returns the list of HOSTRADA file paths for the configured year
    range, sorted chronologically.
    """
    paths = []
    for year in HOSTRADA_YEARS:
        pattern = f"sfcWind_1hr_HOSTRADA-v1-0_BE_gn_{year}*.nc"
        paths.extend(HOSTRADA_DIR.glob(pattern))

    if not paths:
        raise FileNotFoundError(
            f"No HOSTRADA files found in {HOSTRADA_DIR} for years {HOSTRADA_YEARS}. "
            f"Run hostrada_download.py first."
        )

    return sorted(paths)


def _find_nearest_cell(ds: xr.Dataset, coord: Coordinate) -> tuple:
    """
    Finds the (Y, X) index of the HOSTRADA grid cell nearest to the
    given coordinate, using simple squared lat/lon distance.

    Uses nanargmin rather than argmin because HOSTRADA's grid is
    rectangular but Germany's actual shape is not - cells outside
    Germany's land area have lat/lon = NaN, and plain argmin can
    incorrectly select one of these invalid cells.
    """
    dist_sq = (ds["lat"] - coord.lat) ** 2 + (ds["lon"] - coord.lon) ** 2
    y_idx, x_idx = np.unravel_index(np.nanargmin(dist_sq.values), dist_sq.shape)
    return y_idx, x_idx


def get_reference_wind_speed(coord: Coordinate) -> float:
    """
    Returns the multi-year mean near-surface (10 m) wind speed at the
    HOSTRADA grid cell nearest to the given coordinate. This is the
    v_ref value used later in the power law extrapolation.

    Note: this computes one overall mean across the full configured
    year range (HOSTRADA_YEARS), not a mean-of-yearly-means. For a
    clean dataset with no missing hours, the two are expected to be
    nearly identical.
    """
    wind_series = load_wind_speed_timeseries(coord)
    return float(wind_series.mean())

def load_wind_speed_timeseries(coord: Coordinate) -> xr.DataArray:
    file_paths = _get_file_paths()

    ds = xr.open_mfdataset(
        file_paths,
        combine="nested",
        concat_dim="time",
        chunks={"time": 168},
        data_vars="minimal",
        coords="minimal",
        compat="override",
    )

    y_idx, x_idx = _find_nearest_cell(ds, coord)
    wind_series = ds["sfcWind"].isel(Y=y_idx, X=x_idx).load()  # force load into memory now
    ds.close()  # release the full multi-file dataset handle

    return wind_series

if __name__ == "__main__":
    test_coord = Coordinate(lat=52.5200, lon=13.4050)

    print("Finding files...")
    files = _get_file_paths()
    print(f"Found {len(files)} files.")

    print("Loading and extracting wind speed time series (this may take a while)...")
    wind_series = load_wind_speed_timeseries(test_coord)

    print(wind_series)
    print("Number of hourly values:", wind_series.sizes["time"])
    print("Number of NaN values:", int(wind_series.isnull().sum()))

    print("\nComputing reference wind speed (v_ref)...")
    v_ref = float(wind_series.mean())
    print(f"Reference wind speed (v_ref) for Berlin: {v_ref:.3f} m/s")