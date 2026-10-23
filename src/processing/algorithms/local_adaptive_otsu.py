"""NumPy reference implementation of tile-based adaptive Otsu thresholding."""

from dataclasses import dataclass
from math import inf, sqrt

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class AdaptiveOtsuResult:
    """Per-pixel classification and per-tile threshold diagnostics."""

    flood_mask: NDArray[np.bool_]
    threshold_map: NDArray[np.float64]
    median_threshold: float
    tested_tiles: int
    accepted_tiles: int
    fallback: bool


def local_adaptive_otsu(
    values: ArrayLike,
    *,
    tile_shape: tuple[int, int] = (256, 256),
    bins: int = 256,
    minimum_ashman_d: float = 2.0,
    valid_mask: ArrayLike | None = None,
    minimum_valid_pixels: int = 2,
) -> AdaptiveOtsuResult:
    """Classify lower-backscatter pixels using accepted per-tile thresholds.

    A tile is accepted when its two Otsu classes have Ashman's D at least the
    configured value. If none qualify, all valid pixels use global Otsu and
    ``fallback`` is true.
    """
    raster = np.asarray(values, dtype=np.float64)
    if raster.ndim != 2:
        raise ValueError("values must be a 2D raster")
    if (
        len(tile_shape) != 2
        or any(isinstance(size, bool) or not isinstance(size, int) or size < 1 for size in tile_shape)
    ):
        raise ValueError("tile_shape must contain two positive integers")
    if not np.isfinite(minimum_ashman_d) or minimum_ashman_d < 0:
        raise ValueError("minimum_ashman_d must be finite and non-negative")
    if (
        isinstance(minimum_valid_pixels, bool)
        or not isinstance(minimum_valid_pixels, int)
        or minimum_valid_pixels < 2
    ):
        raise ValueError("minimum_valid_pixels must be an integer of at least 2")

    valid = np.isfinite(raster)
    if valid_mask is not None:
        supplied_mask = np.asarray(valid_mask, dtype=np.bool_)
        if supplied_mask.shape != raster.shape:
            raise ValueError("valid_mask must have the same shape as values")
        valid &= supplied_mask
    if not valid.any():
        raise ValueError("values contain no valid samples")

    tile_height, tile_width = tile_shape
    tile_rows = (raster.shape[0] + tile_height - 1) // tile_height
    tile_columns = (raster.shape[1] + tile_width - 1) // tile_width
    threshold_map = np.full((tile_rows, tile_columns), np.nan, dtype=np.float64)
    flood_mask = np.zeros(raster.shape, dtype=np.bool_)
    accepted_thresholds: list[float] = []
    tested_tiles = 0

    for tile_row in range(tile_rows):
        row_start = tile_row * tile_height
        row_end = min(row_start + tile_height, raster.shape[0])
        for tile_column in range(tile_columns):
            column_start = tile_column * tile_width
            column_end = min(column_start + tile_width, raster.shape[1])
            tile = raster[row_start:row_end, column_start:column_end]
            tile_valid = valid[row_start:row_end, column_start:column_end]
            samples = tile[tile_valid]
            if samples.size < minimum_valid_pixels or samples.min() == samples.max():
                continue

            tested_tiles += 1
            threshold = _otsu_threshold(samples, bins)
            lower_class = samples < threshold
            upper_class = ~lower_class
            if not lower_class.any() or not upper_class.any():
                continue

            lower_std = float(samples[lower_class].std())
            upper_std = float(samples[upper_class].std())
            denominator = sqrt(lower_std**2 + upper_std**2)
            ashman_d = (
                inf
                if denominator == 0
                else sqrt(2.0)
                * abs(float(samples[lower_class].mean() - samples[upper_class].mean()))
                / denominator
            )
            if ashman_d < minimum_ashman_d:
                continue

            threshold_map[tile_row, tile_column] = threshold
            accepted_thresholds.append(threshold)
            flood_mask[row_start:row_end, column_start:column_end] = (
                tile_valid & (tile < threshold)
            )

    fallback = not accepted_thresholds
    if fallback:
        global_threshold = _otsu_threshold(raster[valid], bins)
        threshold_map.fill(global_threshold)
        flood_mask = valid & (raster < global_threshold)
        median_threshold = global_threshold
    else:
        median_threshold = float(np.median(accepted_thresholds))

    return AdaptiveOtsuResult(
        flood_mask=flood_mask,
        threshold_map=threshold_map,
        median_threshold=median_threshold,
        tested_tiles=tested_tiles,
        accepted_tiles=len(accepted_thresholds),
        fallback=fallback,
    )


def _otsu_threshold(samples: NDArray[np.float64], bins: int) -> float:
    """Return Otsu's threshold for a non-empty, non-constant sample set."""
    lower = float(samples.min())
    upper = float(samples.max())
    if lower == upper:
        return lower

    counts, edges = np.histogram(samples, bins=bins, range=(lower, upper))
    centers = (edges[:-1] + edges[1:]) / 2.0
    weights_left = np.cumsum(counts, dtype=np.float64)
    weights_right = samples.size - weights_left
    sums_left = np.cumsum(counts * centers, dtype=np.float64)
    total_sum = sums_left[-1]
    means_left = np.divide(
        sums_left,
        weights_left,
        out=np.zeros_like(sums_left),
        where=weights_left > 0,
    )
    means_right = np.divide(
        total_sum - sums_left,
        weights_right,
        out=np.zeros_like(weights_right),
        where=weights_right > 0,
    )
    variance = weights_left * weights_right * (means_left - means_right) ** 2
    variance[(weights_left == 0) | (weights_right == 0)] = -1.0
    split = int(np.argmax(variance))
    return float(edges[split + 1])
