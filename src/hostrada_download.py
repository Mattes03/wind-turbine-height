"""
One-time (or repeatable) script to download HOSTRADA wind speed files
for the configured year range from the DWD Open Data server.
"""

import calendar
import requests

from config import DATA_RAW, HOSTRADA_YEARS

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/hostrada/wind_speed/"
OUTPUT_DIR = DATA_RAW / "hostrada"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_filename(year: int, month: int) -> str:
    last_day = calendar.monthrange(year, month)[1]
    start = f"{year}{month:02d}0100"
    end = f"{year}{month:02d}{last_day}23"
    return f"sfcWind_1hr_HOSTRADA-v1-0_BE_gn_{start}-{end}.nc"


def download_file(filename: str) -> None:
    local_path = OUTPUT_DIR / filename
    if local_path.exists():
        print(f"SKIP (already exists): {filename}")
        return

    url = BASE_URL + filename
    print(f"Downloading: {filename} ...")
    response = requests.get(url, stream=True)
    response.raise_for_status()  # raises an error if the URL 404s or fails

    with open(local_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Done: {filename}")



if __name__ == "__main__":
    for year in HOSTRADA_YEARS:
        for month in range(1, 13):
            filename = build_filename(year, month)
            download_file(filename)