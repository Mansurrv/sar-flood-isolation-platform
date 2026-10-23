import numpy as np
import pytest

from src.processing.algorithms.local_adaptive_otsu import local_adaptive_otsu


def test_accepts_bimodal_tiles_and_classifies_each_locally():
    values = np.array(
        [
            [-20.0, -20.0, -5.0, -5.0],
            [-20.0, -5.0, -5.0, -3.0],
            [-18.0, -18.0, -3.0, -3.0],
            [-18.0, -3.0, -3.0, -1.0],
        ]
    )

    result = local_adaptive_otsu(values, tile_shape=(2, 2), bins=8)

    assert result.tested_tiles == 4
    assert result.accepted_tiles == 4
    assert not result.fallback
    assert result.threshold_map.shape == (2, 2)
    assert result.flood_mask[0, 0]
    assert result.flood_mask[0, 2]
    assert not result.flood_mask[1, 3]


def test_falls_back_to_global_threshold_when_no_tile_is_bimodal():
    values = np.full((4, 4), -10.0)
    values[0, 0] = np.nan

    result = local_adaptive_otsu(values, tile_shape=(2, 2))

    assert result.fallback
    assert result.accepted_tiles == 0
    assert result.tested_tiles == 0
    assert np.isfinite(result.threshold_map).all()
    assert not result.flood_mask.any()


def test_detects_a_five_percent_water_class_in_a_bimodal_tile():
    values = np.full((10, 10), -5.0)
    values.flat[:5] = -20.0

    result = local_adaptive_otsu(values, tile_shape=(10, 10), bins=256)

    assert result.accepted_tiles == 1
    assert not result.fallback
    assert result.flood_mask.sum() == 5
    assert -20.1 <= result.median_threshold <= -19.9


def test_skips_masked_pixels_and_partial_edge_tiles():
    values = np.array(
        [
            [-20.0, -20.0, -5.0],
            [-20.0, -5.0, -3.0],
            [-18.0, -3.0, -3.0],
        ]
    )
    valid = np.ones_like(values, dtype=bool)
    valid[0, 0] = False

    result = local_adaptive_otsu(
        values, tile_shape=(2, 2), bins=8, valid_mask=valid
    )

    assert result.threshold_map.shape == (2, 2)
    assert not result.flood_mask[0, 0]
    assert result.tested_tiles == 3


@pytest.mark.parametrize(
    ("values", "kwargs", "message"),
    [
        (np.ones(5), {}, "2D raster"),
        (np.ones((2, 2)), {"tile_shape": (0, 2)}, "positive integers"),
        (np.ones((2, 2)), {"minimum_ashman_d": -1}, "non-negative"),
        (np.full((2, 2), np.nan), {}, "no valid samples"),
        (np.ones((2, 2)), {"valid_mask": np.ones(3)}, "same shape"),
    ],
)
def test_rejects_invalid_inputs(values, kwargs, message):
    with pytest.raises(ValueError, match=message):
        local_adaptive_otsu(values, **kwargs)
