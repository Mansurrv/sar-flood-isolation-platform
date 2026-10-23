"""Polarisation combination and threshold sensitivity reference algorithms."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray

PolarizationMode = str


@dataclass(frozen=True)
class SensitivityResult:
    """Masks and flooded-pixel counts indexed by mode and dB offset."""

    masks: dict[tuple[PolarizationMode, float], NDArray[np.bool_]]
    flooded_pixel_counts: dict[tuple[PolarizationMode, float], int]


def run_threshold_sensitivity(
    vv: ArrayLike,
    vh: ArrayLike,
    *,
    vv_threshold_db: float,
    vh_threshold_db: float,
    offsets_db: tuple[float, ...] = (-1.0, 0.0, 1.0),
    valid_mask: ArrayLike | None = None,
) -> SensitivityResult:
    """Create VV, VH, AND and OR masks for each threshold offset.

    Water is defined as backscatter strictly below threshold plus offset.
    Invalid pixels are false in every mask.
    """
    vv_array = np.asarray(vv, dtype=np.float64)
    vh_array = np.asarray(vh, dtype=np.float64)
    if vv_array.ndim == 0 or vv_array.shape != vh_array.shape:
        raise ValueError("VV and VH arrays must have matching array shapes")
    if not np.isfinite(vv_threshold_db) or not np.isfinite(vh_threshold_db):
        raise ValueError("polarisation thresholds must be finite")
    if not offsets_db:
        raise ValueError("offsets_db must contain at least one offset")
    if any(not np.isfinite(offset) for offset in offsets_db):
        raise ValueError("offsets_db values must be finite")
    if len(set(offsets_db)) != len(offsets_db):
        raise ValueError("offsets_db values must be unique")

    valid = np.isfinite(vv_array) & np.isfinite(vh_array)
    if valid_mask is not None:
        supplied_mask = np.asarray(valid_mask, dtype=np.bool_)
        if supplied_mask.shape != vv_array.shape:
            raise ValueError("valid_mask must have the same shape as VV and VH")
        valid &= supplied_mask

    masks: dict[tuple[PolarizationMode, float], NDArray[np.bool_]] = {}
    counts: dict[tuple[PolarizationMode, float], int] = {}
    for offset in offsets_db:
        vv_mask = valid & (vv_array < vv_threshold_db + offset)
        vh_mask = valid & (vh_array < vh_threshold_db + offset)
        combined = {
            "VV": vv_mask,
            "VH": vh_mask,
            "AND": vv_mask & vh_mask,
            "OR": vv_mask | vh_mask,
        }
        for mode, mask in combined.items():
            key = (mode, float(offset))
            masks[key] = mask.copy()
            counts[key] = int(mask.sum())

    return SensitivityResult(masks, counts)
