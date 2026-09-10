# Wind Turbine Hub Height Estimator
The project uses real climate and land cover data to estimate the wind 
profile at any coordinate in Germany. 
The wind profile is done to support early planning steps of wind 
turbines, providing data to estimate a needed hub height. 

---

## 1. Project summary

Choosing a wind turbine's hub height is a trade-off: wind speed
generally increases with height, but so do construction costs. This
project builds a reproducible Python workflow that, given any
coordinate in Germany, estimates how wind speed changes with height
above ground - the **wind profile** - using real climate data and
local land cover information.

The project produces:

- The 10-year mean near-surface (10 m) reference wind speed for the
  input coordinate, from the DWD HOSTRADA dataset.
- The local land cover class at that coordinate, from the LBM-DE2021
  dataset, translated into a roughness-based shear exponent (alpha).
- A calculated wind profile (wind speed at heights from 50 m to
  200 m), using Hellmann's power law.
- A combined PDF report with the calculation method, a results table,
  and a plot, saved per coordinate under `data/processed/`.

---

## 2. Environmental engineering motivation

Estimating wind speed at different heights is a core step in
assessing wind energy potential:

- **Site assessment** - before a wind turbine is built, the expected
  wind resource at hub height must be estimated from data measured
  much closer to the ground.
- **Hub height trade-offs** - taller towers generally capture higher,
  steadier wind speeds, but building and maintaining a taller tower
  costs more. Quantifying the wind speed gain per meter of height
  supports that trade-off.
- **Land cover effects on wind flow** - surface roughness (open
  farmland vs. forest vs. urban area) strongly affects how quickly
  wind speed increases with height, so local land cover cannot be
  ignored in a serious site assessment.
- **Reproducible resource assessment** - using open government data
  (DWD, BKG) instead of proprietary wind atlases makes the workflow
  transparent, checkable and freely repeatable for any location in
  Germany.

---

## 3. Business / project-style problem statement

> **Context.** 
> Potential onshore sites for wind turbines are identified based on
> factors such as distance from residential areas, land costs, soil 
> conditions, and the local flora and fauna. As part of these early
> planning steps, a broad overview of the wind profile in these 
> locations is necessary. The team needs a quick tool to estimate how
> much wind is available and how high the wind turbine possibly needs
> to be for further planning purposes. 

> **Question.** 
> Given a coordinate, what wind speed can be expected at typical wind
> turbine hub heights (50-200 m)?
>
> **Deliverable.** A reproducible Python project that takes a
> coordinate, collects real 10-year wind and land cover data,
> calculates a wind profile, and reports the result as a clear table,
> plot and PDF summary.

---

## 4. Datasets

### 4.1 HOSTRADA (wind speed)

- Source: Deutscher Wetterdienst (DWD), Climate Data Center.
- Product: HOSTRADA - Hochaufgeloester Stuendlicher Rasterdatensatz
  fuer Deutschland, hourly near-surface wind speed, 1 km x 1 km grid,
  ETRS89 / LCC Europe (EPSG:3034), available from 1995 to present.
- Download: <https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/hostrada/wind_speed/>
- **Not committed** to the repository (~20 GB for a 10-year window).
  Downloaded locally via `src/hostrada_download.py`.

### 4.2 LBM-DE2021 (land cover)

- Source: Bundesamt fuer Kartographie und Geodaesie (BKG).
- Product: Digitales Landbedeckungsmodell Deutschland, reference year
  2021, 1 ha minimum mapping unit, CORINE Land Cover (CLC)
  nomenclature, CRS: EPSG:25832 (UTM Zone 32N).
- Download: <https://gdz.bkg.bund.de/index.php/default/digitales-landbedeckungsmodell-deutschland-stand-2021-lbm-de.html>
- **Not committed** to the repository (~5.9 GB).
 Downloaded and extracted automatically via `src/lbm_download.py`.

### 4.3 Germany border (coordinate validation)

- A country border polygon (Natural Earth Admin-0 Countries,
  filtered to Germany) used to confirm an input coordinate actually
  lies inside Germany, not just inside its bounding box.
- **Not committed** to the repository (~4.7 MB). Downloaded and
  extracted automatically via `src/border_download.py`.

### 4.4 Roughness length lookup

- CLC code -> roughness length (z0) values from Silva et al.,
  "Roughness length classification of Corine land cover classes",
  used to derive the shear exponent (alpha) for each land cover type.
  See `CLC_Z0_LOOKUP` in `src/config.py`.

---

## 5. Project structure

```
wind-turbine-height/
│
├── data/
│   ├── raw/
│   │   ├── hostrada/           # HOSTRADA monthly .nc files (not committed)
│   │   ├── LBM/                # LBM-DE2021 geopackage (not committed)
│   │   └── ShapeGermany/       # Germany border shapefile
│   └── processed/              # one subfolder per coordinate, with
│                                # wind_profile.csv, wind_profile.png,
│                                # summary.txt and report.pdf
│
├── notebooks/
│   └── 00_check_environment.ipynb   # environment and data checks
│
├── src/
│   ├── config.py                # paths, constants, lookup tables
│   ├── border_download.py       # one-time download of Germany border shapefile
│   ├── hostrada_download.py     # one-time download of HOSTRADA files
│   ├── lbm_download.py          # one-time download of LBM-DE2021
│   ├── coordinates.py           # coordinate validation (Germany border check)
│   ├── hostrada_prep.py         # HOSTRADA loading + reference wind speed (v_ref)
│   ├── lbm_prep.py              # LBM-DE2021 land cover lookup (CLC code)
│   ├── alpha_calculation.py     # roughness length -> shear exponent (alpha)
│   ├── wind_profile.py          # power law calculation across height range
│   └── visualization.py         # table, plot, and combined PDF report
│
├── .gitignore
├── README.md                    # <-- main documentation
├── requirements.txt
└── main.py                      # main entry point
```

---

## 6. Setup instructions (Windows, PowerShell)

Open a terminal in the project folder and run:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> If you re-open the project later, simply run
> `venv\Scripts\activate` from the project folder to re-activate the
> virtual environment.

### 6.1 Download the required datasets

1. **HOSTRADA**: run the download script once (this takes a while
   and downloads ~20 GB for the configured 10-year window):
   ```powershell
   cd src
   python hostrada_download.py
   ```
2. **LBM-DE2021**: run the download script once (downloads a ~2.1 GB
   zip and extracts the ~5.9 GB geopackage):
```powershell
   cd src
   python lbm_download.py
```
3. **Germany border shapefile**: run the download script once
   (downloads and extracts a small ~4.7 MB shapefile):
```powershell
   cd src
   python border_download.py
```
---

## 7. How to run the project in VS Code

1. Open the project folder in VS Code.
2. Open a terminal (`Terminal -> New Terminal`).
3. Activate the virtual environment:
   ```powershell
   venv\Scripts\activate
   ```
4. (Optional) Open `notebooks/00_check_environment.ipynb` and run the
   cells to verify the environment and the datasets are set up
   correctly.
5. Open `main.py` and set the coordinate you want to analyze:
   ```python
   LAT = 52.5200
   LON = 13.4050
   ```
6. Run the main script:
   ```powershell
   python main.py
   ```
7. Check the results in `data/processed/<lat>_<lon>/`:
   - `wind_profile.csv` - the height/wind speed table
   - `wind_profile.png` - the plot
   - `summary.txt` - a short text summary
   - `report.pdf` - a combined report with heading, explanation,
     table and plot

> **Note:** the first run for a new coordinate takes a longer time,
> since it opens all configured HOSTRADA files (one per month, see
> `HOSTRADA_YEARS` in `src/config.py`) to compute the 10-year mean
> reference wind speed.

---

## 8. Workflow

```
Coordinate (lat, lon)
        │
        ▼
  coordinates.py       ─►  validated coordinate (inside Germany)
        │
        ├──────────────────────────────┐
        ▼                              ▼
  hostrada_prep.py              lbm_prep.py
  (10-year mean wind             (CLC land cover
   speed at 10 m, v_ref)          code)
        │                              │
        │                              ▼
        │                     alpha_calculation.py
        │                     (roughness length z0
        │                      -> shear exponent alpha)
        │                              │
        └──────────────┬───────────────┘
                        ▼
                 wind_profile.py
          (Hellmann's power law across
           the configured height range)
                        │
                        ▼
                visualization.py
        (table, plot, combined PDF report)
                        │
                        ▼
        data/processed/<lat>_<lon>/
```

`main.py` is the orchestrator. It calls the functions from the `src/`
package in the order above.

---

## 9. Calculation method

Wind speed at a target height `h` is estimated from the 10 m
reference wind speed `v_ref` using **Hellmann's power law**:

```
v(h) = v_ref * (h / h_ref) ** alpha
```

where `h_ref = 10 m` (the HOSTRADA reference height).

The shear exponent `alpha` is derived from the roughness length `z0`
of the local land cover class:

```
alpha = 1 / ln(z_ref / z0)
```

`z0` is looked up from the CLC land cover code (see section 4.4) at
the input coordinate, using LBM-DE2021.

---

## 10. Results produced by the project

After running `python main.py` you will see, for the given
coordinate:

- A terminal printout with the calculated wind profile:
  ```
  Height (m) | Wind speed (m/s)
  --------------------------------
          50 | ...
          60 | ...
         ...
         200 | ...
  ```
- A combined PDF report (`report.pdf`) containing the reference wind
  speed, the shear exponent and land cover class used, the full
  table, and a plot of the wind profile.

---

## 11. Limitations

- The power law with a single, land-cover-derived shear exponent is
  a simplification; it does not account for atmospheric stability,
  time-of-day or seasonal effects on the wind profile.
- HOSTRADA and LBM-DE2021 are both gridded/mapped products, not
  point measurements; the nearest 1 km grid cell (HOSTRADA) or 1 ha
  polygon (LBM-DE) is used as an approximation for the exact input
  coordinate.
- The project does not currently include a hub height recommendation,
  since no sufficiently robust literature basis for a general
  recommendation rule was identified within the project scope.

---

## 12. Future extension

The project is intentionally focused on the wind profile calculation,
but it is structured so that further analysis can be added without
rewriting the core pipeline:

- `src/wind_profile.py` already isolates the power law calculation,
  so a logarithmic wind profile (using z0 directly) could be added
  and compared against it.
- Wind power density (proportional to wind speed cubed) could be
  added as an additional column/plot using the existing profile
  output.
- Multiple coordinates could be compared on a single plot by calling
  `wind_profile.calculate_wind_profile()` for each and combining the
  results in `visualization.py`.

---

## 13. References

- Deutscher Wetterdienst (DWD). *HOSTRADA - Hochaufgeloester
  Stuendlicher Rasterdatensatz fuer Deutschland.*
  <https://opendata.dwd.de/climate_environment/CDC/grids_germany/hourly/hostrada/>
- Bundesamt fuer Kartographie und Geodaesie (BKG). *Digitales
  Landbedeckungsmodell Deutschland (LBM-DE), Stand 2021.*
  <https://gdz.bkg.bund.de/index.php/default/digitales-landbedeckungsmodell-deutschland-stand-2021-lbm-de.html>
- Silva, J., et al. *Roughness length classification of Corine land
  cover classes.*
- Gualtieri, G. & Secci, S. (2012). *Methods to extrapolate wind
  resource to the turbine hub height based on power law: A 1-h wind
  speed vs. Weibull distribution extrapolation comparison.*
  Renewable Energy, 43, 183-200.
- IEC 61400-1. *Wind turbines - Part 1: Design requirements.*
