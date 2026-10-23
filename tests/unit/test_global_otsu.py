import numpy as np
import pytest

from src.processing.algorithms.global_otsu import global_otsu


def test_finds_threshold_between_two_backscatter_classes():
    values = np.array([-20.0] * 50 + [-5.0] * 50)

    result = global_otsu(values, bins=256)

    expected_first_split = -20.0 + 15.0 / 256.0
    assert result.threshold == pytest.approx(expected_first_split, abs=0.1)
    assert result.flood_mask[:50].all()
    assert not result.flood_mask[50:].any()
    assert result.valid_count == 100


def test_ignores_nonfinite_and_masked_cells():
    values = np.array([[-18.0, -17.0], [-4.0, np.nan]])
    valid_mask = np.array([[True, False], [True, True]])

    result = global_otsu(values, valid_mask=valid_mask)

    assert result.valid_count == 2
    assert result.flood_mask.tolist() == [[True, False], [False, False]]


def test_constant_input_returns_the_constant_and_no_flood_pixels():
    result = global_otsu(np.full((2, 3), -12.0))

    assert result.threshold == -12.0
    assert not result.flood_mask.any()


@pytest.mark.parametrize(
    ("values", "kwargs", "message"),
    [
        ([np.nan, np.inf], {}, "no valid samples"),
        ([1.0, 2.0], {"bins": 0}, "positive integer"),
        ([1.0, 2.0], {"value_range": (2.0, 1.0)}, "increasing bounds"),
        ([1.0, 2.0], {"value_range": (0.0, 1.5)}, "include all valid samples"),
        ([1.0, 2.0], {"valid_mask": [True]}, "same shape"),
    ],
)
def test_invalid_inputs_raise_clear_value_error(values, kwargs, message):
    with pytest.raises(ValueError, match=message):
        global_otsu(values, **kwargs)


def test_equal_variance_ties_choose_lowest_split_deterministically():
    values = np.array([-10.0, -8.0, -2.0, 0.0])

    first = global_otsu(values, bins=4)
    second = global_otsu(values, bins=4)

    assert first.threshold == second.threshold
    np.testing.assert_array_equal(first.flood_mask, second.flood_mask)
