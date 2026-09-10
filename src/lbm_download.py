"""
One-time script to download the LBM-DE2021 land cover dataset from
BKG's direct-download server and extract the .gpkg file from the zip.
"""

import zipfile

import requests

from config import DATA_RAW

DOWNLOAD_URL = "https://daten.gdz.bkg.bund.de/produkte/dlm/lbm-de_2021/aktuell/lbm-de2021.utm32s.gpkg.zip"
OUTPUT_DIR = DATA_RAW / "LBM"
ZIP_PATH = OUTPUT_DIR / "lbm-de2021.utm32s.gpkg.zip"
GPKG_PATH = OUTPUT_DIR / "LBMDE.gpkg"


def download_zip() -> None:
    """
    Downloads the LBM-DE2021 zip file, if the final .gpkg doesn't
    already exist and the zip isn't already downloaded.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if GPKG_PATH.exists():
        print(f"SKIP download (final file already exists): {GPKG_PATH.name}")
        return

    if ZIP_PATH.exists():
        print(f"SKIP (zip already exists): {ZIP_PATH.name}")
        return

    print(f"Downloading {DOWNLOAD_URL} ...")
    print("This is a ~2.1 GB file - this will take a while.")
    response = requests.get(DOWNLOAD_URL, stream=True)
    response.raise_for_status()

    with open(ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete.")


def extract_gpkg() -> None:
    """
    Extracts the .gpkg file from the downloaded zip, and renames it
    to LBMDE.gpkg to match the filename expected by lbm_prep.py.
    """
    if GPKG_PATH.exists():
        print(f"SKIP (already exists): {GPKG_PATH.name}")
        return

    print("Extracting .gpkg file from zip (this may also take a while) ...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        gpkg_names = [name for name in zf.namelist() if name.endswith(".gpkg")]
        if not gpkg_names:
            raise FileNotFoundError("No .gpkg file found inside the downloaded zip.")

        zf.extract(gpkg_names[0], path=OUTPUT_DIR)

        extracted_path = OUTPUT_DIR / gpkg_names[0]
        extracted_path.rename(GPKG_PATH)

    print(f"Extracted to: {GPKG_PATH}")

if __name__ == "__main__":
    if GPKG_PATH.exists():
        print(f"LBM-DE2021 already set up at: {GPKG_PATH}")
    else:
        download_zip()
        extract_gpkg()
        print("\nDone. LBM-DE2021 is ready at:", GPKG_PATH)