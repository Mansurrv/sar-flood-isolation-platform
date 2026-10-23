"""NumPy reference implementation of global Otsu flood thresholding."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class OtsuResult:
    """Threshold and classification for one backscatter raster."""

    threshold: float
    flood_mask: NDArray[np.bool_]
    valid_count: int


def global_otsu(
    values: ArrayLike,
    *,
    bins: int = 256,
    value_range: tuple[float, float] | None = None,
    valid_mask: ArrayLike | None = None,
) -> OtsuResult:
    """Compute a global Otsu threshold and classify lower values as water.

    Ties between equally optimal thresholds are resolved by selecting the
    first (lowest) histogram split. Invalid and masked cells are false in the
    returned flood mask.
    """
    raster = np.asarray(values, dtype=np.float64)
    if raster.ndim == 0:
        raise ValueError("values must be an array")
    if isinstance(bins, bool) or not isinstance(bins, int) or bins < 1:
        raise ValueError("bins must be a positive integer")

    valid = np.isfinite(raster)
    if valid_mask is not None:
        supplied_mask = np.asarray(valid_mask, dtype=np.bool_)
        if supplied_mask.shape != raster.shape:
            raise ValueError("valid_mask must have the same shape as values")
        valid &= supplied_mask

    samples = raster[valid]
    if samples.size == 0:
        raise ValueError("values contain no valid samples")

    minimum = float(samples.min())
    maximum = float(samples.max())
    if value_range is None:
        lower, upper = minimum, maximum
    else:
        if len(value_range) != 2:
            raise ValueError("value_range must contain lower and upper bounds")
        lower, upper = map(float, value_range)
        if not np.isfinite(lower) or not np.isfinite(upper) or lower >= upper:
            raise ValueError("value_range must contain finite increasing bounds")
        if minimum < lower or maximum > upper:
            raise ValueError("value_range must include all valid samples")

    if minimum == maximum:
        threshold = minimum
    else:
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
        between_class_variance = (
            weights_left * weights_right * (means_left - means_right) ** 2
        )
        between_class_variance[weights_left == 0] = -1.0
        between_class_variance[weights_right == 0] = -1.0
        split = int(np.argmax(between_class_variance))
        threshold = float(edges[split + 1])

    flood_mask = valid & (raster < threshold)
    return OtsuResult(threshold, flood_mask, int(samples.size))
