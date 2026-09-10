"""
One-time script to download the Natural Earth Admin-0 Countries
shapefile, used by coordinates.py for precise Germany border
validation.

The downloaded file contains all world countries (despite typically
being renamed "Germany.shp" in this project) - coordinates.py
filters it down to the Germany row using the SOVEREIGNT column.
"""

import zipfile

import requests

from config import DATA_RAW

DOWNLOAD_URL = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_admin_0_countries.zip"
OUTPUT_DIR = DATA_RAW / "ShapeGermany"
ZIP_PATH = OUTPUT_DIR / "ne_10m_admin_0_countries.zip"
SHP_PATH = OUTPUT_DIR / "Germany.shp"


def download_zip() -> None:
    """
    Downloads the Natural Earth countries shapefile zip, if the final
    .shp doesn't already exist and the zip isn't already downloaded.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if SHP_PATH.exists():
        print(f"SKIP download (final file already exists): {SHP_PATH.name}")
        return

    if ZIP_PATH.exists():
        print(f"SKIP (zip already exists): {ZIP_PATH.name}")
        return

    print(f"Downloading {DOWNLOAD_URL} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    response = requests.get(DOWNLOAD_URL, headers=headers, stream=True)
    response.raise_for_status()

    with open(ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")


def extract_shapefile() -> None:
    """
    Extracts all shapefile parts (.shp, .dbf, .shx, .prj, etc.) from
    the downloaded zip, renaming each to Germany.<ext> to match the
    filename expected by coordinates.py.
    """
    if SHP_PATH.exists():
        print(f"SKIP (already exists): {SHP_PATH.name}")
        return

    print("Extracting shapefile parts from zip ...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        # The shapefile consists of several files sharing the same
        # base name with different extensions - extract all of them.
        member_names = [
            name for name in zf.namelist()
            if name.startswith("ne_10m_admin_0_countries.")
        ]
        if not member_names:
            raise FileNotFoundError("No matching shapefile parts found inside the zip.")

        for name in member_names:
            zf.extract(name, path=OUTPUT_DIR)
            extension = name.split(".")[-1]
            extracted_path = OUTPUT_DIR / name
            renamed_path = OUTPUT_DIR / f"Germany.{extension}"
            extracted_path.rename(renamed_path)

    print(f"Extracted to: {SHP_PATH}")


if __name__ == "__main__":
    if SHP_PATH.exists():
        print(f"Germany border shapefile already set up at: {SHP_PATH}")
    else:
        download_zip()
        extract_shapefile()
        print("\nDone. Germany border shapefile is ready at:", SHP_PATH)