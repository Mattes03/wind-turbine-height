"""
Displays a calculated wind profile (height -> wind speed) as both a
formatted table (printed to the console) and a graphical plot, and
saves the table (CSV), the plot (PNG), and a short summary (including
v_ref) into a coordinate-specific subfolder under data/processed/.
Also creates a single combined PDF report with heading, explanation,
table, and plot.
"""

import csv

import matplotlib.pyplot as plt

from config import DATA_PROCESSED, CLC_CLASS_NAMES, DEFAULT_CLASS_NAME
from coordinates import Coordinate
from wind_profile import calculate_wind_profile


def _get_output_paths(coord: Coordinate) -> dict:
    """
    Returns output file paths inside a coordinate-specific subfolder
    of data/processed/, so results from different coordinates are
    kept in separate folders rather than mixed together by filename.
    """
    folder_name = f"{coord.lat:.4f}_{coord.lon:.4f}"
    output_folder = DATA_PROCESSED / folder_name
    output_folder.mkdir(parents=True, exist_ok=True)

    return {
        "csv": output_folder / "wind_profile.csv",
        "png": output_folder / "wind_profile.png",
        "summary": output_folder / "summary.txt",
    }


def print_profile_table(profile: dict) -> None:
    """
    Prints the wind profile as a simple formatted table.
    """
    print("\nHeight (m) | Wind speed (m/s)")
    print("-" * 32)
    for height, speed in profile.items():
        print(f"{height:>10} | {speed:.3f}")


def save_profile_csv(profile: dict, csv_path) -> None:
    """
    Saves the wind profile as a CSV file with two columns:
    height_m, wind_speed_m_s.
    """
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["height_m", "wind_speed_m_s"])
        for height, speed in profile.items():
            writer.writerow([height, round(speed, 3)])
    print(f"Table saved to: {csv_path}")


def save_summary(coord: Coordinate, v_ref: float, summary_path) -> None:
    """
    Saves a short text summary including the coordinate and the
    calculated reference wind speed (v_ref).
    """
    with open(summary_path, "w") as f:
        f.write(f"Coordinate: lat={coord.lat}, lon={coord.lon}\n")
        f.write(f"Reference wind speed (v_ref, 10m): {v_ref:.3f} m/s\n")
    print(f"Summary saved to: {summary_path}")


def plot_profile(profile: dict, coord: Coordinate, save_path=None) -> None:
    """
    Plots the wind profile as height (y-axis) vs. wind speed (x-axis).
    If save_path is given, saves the figure to that path in addition
    to displaying it.
    """
    heights = list(profile.keys())
    speeds = list(profile.values())

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.plot(speeds, heights, marker="o", linestyle="-", color="tab:blue")

    ax.set_xlabel("Wind speed (m/s)")
    ax.set_ylabel("Height above ground (m)")
    ax.set_title(f"Wind profile at ({coord.lat:.4f}, {coord.lon:.4f})")
    ax.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
        print(f"Plot saved to: {save_path}")

    plt.show()


def create_report(profile: dict, coord: Coordinate, v_ref: float, alpha: float, clc_code: int, save_path) -> None:
    """
    Creates a single combined PDF report containing a heading, a short
    explanation of v_ref and the power law method used (including the
    alpha value and the land cover class it was derived from), the
    wind profile table, and the plot.
    """
    class_name = CLC_CLASS_NAMES.get(clc_code, DEFAULT_CLASS_NAME)

    fig = plt.figure(figsize=(8.5, 11))
    gs = fig.add_gridspec(nrows=4, ncols=1, height_ratios=[0.3, 1.4, 2.9, 4.3])

    # --- Heading ---
    ax_title = fig.add_subplot(gs[0])
    ax_title.axis("off")
    ax_title.text(
        0.5, 0.5,
        f"Wind Speed Information for ({coord.lat:.4f}, {coord.lon:.4f})",
        fontsize=16, fontweight="bold", ha="center", va="center",
    )

    # --- Explanatory text ---
    ax_text = fig.add_subplot(gs[1])
    ax_text.axis("off")
    explanation = (
        f"The reference wind speed at 10 m height, v_ref = {v_ref:.3f} m/s, was calculated "
        f"as the mean hourly wind speed from HOSTRADA data over a multi-year period at the "
        f"grid cell nearest to this coordinate.\n\n"
        f"Wind speed at other heights was estimated using Hellmann's power law, "
        f"v(h) = v_ref * (h / h_ref)^alpha, with a shear exponent of alpha = {alpha:.4f}.\n\n"
        f"This alpha value was derived from the local land cover class at this coordinate: "
        f"CLC code {clc_code} - \"{class_name}\" (source: LBM-DE2021)."
    )
    ax_text.text(0.02, 1.0, explanation, fontsize=10, ha="left", va="top", wrap=True)

    # --- Table ---
    ax_table = fig.add_subplot(gs[2])
    ax_table.axis("off")
    ax_table.set_title("Calculated Wind Speed by Height", fontsize=12, fontweight="bold", pad=20)

    table_data = [["Height (m)", "Wind speed (m/s)"]]
    for height, speed in profile.items():
        table_data.append([str(height), f"{speed:.3f}"])

    table = ax_table.table(cellText=table_data, cellLoc="center", loc="upper center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.2)

    # --- Plot ---
    ax_plot = fig.add_subplot(gs[3])
    ax_plot.set_title("Wind Profile", fontsize=12, fontweight="bold")
    heights = list(profile.keys())
    speeds = list(profile.values())
    ax_plot.plot(speeds, heights, marker="o", linestyle="-", color="tab:blue")
    ax_plot.set_xlabel("Wind speed (m/s)")
    ax_plot.set_ylabel("Height above ground (m)")
    ax_plot.grid(True, linestyle="--", alpha=0.5)

    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    print(f"Report saved to: {save_path}")
    plt.close(fig)


if __name__ == "__main__":
    # Manual smoke test using the same Berlin coordinate as before.
    test_coord = Coordinate(lat=52.5200, lon=13.4050)  # Berlin

    print(f"Calculating wind profile for {test_coord} ...")
    profile, v_ref, alpha, clc_code = calculate_wind_profile(test_coord)

    paths = _get_output_paths(test_coord)

    print_profile_table(profile)
    save_profile_csv(profile, paths["csv"])
    save_summary(test_coord, v_ref, paths["summary"])
    plot_profile(profile, test_coord, save_path=paths["png"])

    report_path = paths["csv"].parent / "report.pdf"
    create_report(profile, test_coord, v_ref, alpha, clc_code, report_path)