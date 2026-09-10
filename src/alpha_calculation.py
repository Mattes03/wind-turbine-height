"""
Calculates the shear exponent alpha for a given coordinate, based on
the CLC land cover code (from lbm_prep.py) and its corresponding
roughness length z0 (from CLC_Z0_LOOKUP in config.py).

Uses alpha = 1 / ln(z_ref / z0), with z_ref fixed at the HOSTRADA
reference height (10 m).
"""

import math

from config import CLC_Z0_LOOKUP, DEFAULT_Z0, HOSTRADA_REFERENCE_HEIGHT_M
from coordinates import Coordinate
from lbm_prep import get_clc_code


def get_roughness_length(clc_code: int) -> float:
    """
    Returns the roughness length z0 (in metres) for a given CLC code,
    using CLC_Z0_LOOKUP. Falls back to DEFAULT_Z0 if the code is not
    found in the lookup table.
    """
    return CLC_Z0_LOOKUP.get(clc_code, DEFAULT_Z0)


def calculate_alpha(z0: float, z_ref: float = HOSTRADA_REFERENCE_HEIGHT_M) -> float:
    """
    Calculates the shear exponent alpha from a roughness length z0,
    using alpha = 1 / ln(z_ref / z0).

    Raises a ValueError if z0 equals z_ref (which would make the
    denominator ln(1) = 0). Not expected to occur with the current
    CLC_Z0_LOOKUP values (max z0 = 1.2 m, far below the 10 m z_ref),
    but guarded against for robustness against future data changes.
    """
    if z0 <= 0:
        raise ValueError(f"z0 must be positive, got {z0}.")
    if z0 == z_ref:
        raise ValueError(
            f"z0 ({z0} m) equals z_ref ({z_ref} m), which would cause "
            f"division by zero (ln(1) = 0) in the alpha calculation."
        )

    return 1 / math.log(z_ref / z0)


def get_alpha_for_coordinate(coord: Coordinate) -> tuple:
    """
    Full pipeline step: takes a coordinate, looks up its CLC land
    cover code, converts that to a roughness length z0, and returns
    the resulting shear exponent alpha along with the CLC code used.

    Returns: (alpha: float, clc_code: int)
    """
    clc_code = get_clc_code(coord)
    z0 = get_roughness_length(clc_code)
    alpha = calculate_alpha(z0)
    return alpha, clc_code


if __name__ == "__main__":
    # Manual smoke test using the same two locations already verified
    # in lbm_prep.py - Berlin (urban) and Großer Rachel (forest) -
    # to confirm alpha comes out meaningfully different for each.
    test_cases = [
        (Coordinate(lat=52.5200, lon=13.4050), "Berlin (urban)"),
        (Coordinate(lat=48.9989, lon=13.4014), "Großer Rachel (forest)"),
    ]

    for coord, description in test_cases:
        clc_code = get_clc_code(coord)
        z0 = get_roughness_length(clc_code)
        alpha = calculate_alpha(z0)
        print(f"{description}: CLC={clc_code}, z0={z0} m, alpha={alpha:.4f}")