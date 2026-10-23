"""NumPy reference implementation of baseline SAR change detection."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class ChangeDetectionResult:
    """Flood candidates and pre/post change diagnostics."""

    flood_mask: NDArray[np.bool_]
    change_db: NDArray[np.float64]
    valid_mask: NDArray[np.bool_]


def baseline_change_detection(
    pre_flood: ArrayLike,
    post_flood: ArrayLike,
    *,
    change_threshold_db: float = -3.0,
    post_flood_cap_db: float = -15.0,
    valid_mask: ArrayLike | None = None,
) -> ChangeDetectionResult:
    """Classify newly darkened pixels as flood candidates.

    ``change_db`` is post-flood minus pre-flood backscatter. Invalid cells are
    NaN in the change raster and false in the flood mask.
    """
    pre = np.asarray(pre_flood, dtype=np.float64)
    post = np.asarray(post_flood, dtype=np.float64)
    if pre.ndim == 0 or post.ndim == 0 or pre.shape != post.shape:
        raise ValueError("pre_flood and post_flood must have matching array shapes")
    if not np.isfinite(change_threshold_db) or not np.isfinite(post_flood_cap_db):
        raise ValueError("threshold and cap must be finite")

    valid = np.isfinite(pre) & np.isfinite(post)
    if valid_mask is not None:
        supplied_mask = np.asarray(valid_mask, dtype=np.bool_)
        if supplied_mask.shape != pre.shape:
            raise ValueError("valid_mask must have the same shape as the rasters")
        valid &= supplied_mask

    change = np.full(pre.shape, np.nan, dtype=np.float64)
    np.subtract(post, pre, out=change, where=valid)
    flood_mask = valid & (change < change_threshold_db) & (
        post < post_flood_cap_db
    )
    return ChangeDetectionResult(flood_mask, change, valid)
