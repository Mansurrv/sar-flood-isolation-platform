import numpy as np
import pytest

from src.processing.algorithms.polarization_sensitivity import (
    run_threshold_sensitivity,
)


def test_generates_all_modes_and_offsets_with_expected_logic():
    vv = np.array([[-20.0, -15.0], [-10.0, -5.0]])
    vh = np.array([[-5.0, -20.0], [-10.0, -15.0]])

    result = run_threshold_sensitivity(
        vv, vh, vv_threshold_db=-12.0, vh_threshold_db=-12.0
    )

    assert len(result.masks) == 12
    np.testing.assert_array_equal(
        result.masks[("AND", 0.0)], [[False, True], [False, False]]
    )
    np.testing.assert_array_equal(
        result.masks[("OR", 0.0)], [[True, True], [False, True]]
    )
    assert result.flooded_pixel_counts[("OR", 0.0)] == 3


def test_mask_subset_and_offset_monotonicity_invariants():
    vv = np.array([[-20.0, -15.0, -10.0, -5.0]])
    vh = np.array([[-18.0, -13.0, -8.0, -3.0]])

    result = run_threshold_sensitivity(
        vv, vh, vv_threshold_db=-12.0, vh_threshold_db=-12.0
    )

    for offset in (-1.0, 0.0, 1.0):
        vv_mask = result.masks[("VV", offset)]
        vh_mask = result.masks[("VH", offset)]
        and_mask = result.masks[("AND", offset)]
        or_mask = result.masks[("OR", offset)]
        assert np.all(and_mask <= vv_mask)
        assert np.all(and_mask <= vh_mask)
        assert np.all(vv_mask <= or_mask)
        assert np.all(vh_mask <= or_mask)
    for mode in ("VV", "VH", "AND", "OR"):
        assert (
            result.flooded_pixel_counts[(mode, -1.0)]
            <= result.flooded_pixel_counts[(mode, 0.0)]
            <= result.flooded_pixel_counts[(mode, 1.0)]
        )


def test_invalid_cells_are_excluded_and_inputs_are_not_mutated():
    vv = np.array([-20.0, np.nan])
    vh = np.array([-20.0, -20.0])
    before_vv = vv.copy()
    before_vh = vh.copy()

    result = run_threshold_sensitivity(
        vv, vh, vv_threshold_db=-12.0, vh_threshold_db=-12.0
    )

    assert result.masks[("AND", 0.0)].tolist() == [True, False]
    np.testing.assert_equal(vv, before_vv)
    np.testing.assert_equal(vh, before_vh)


@pytest.mark.parametrize(
    ("vv", "vh", "kwargs", "message"),
    [
        ([1.0], [[1.0]], {}, "matching array shapes"),
        ([1.0], [2.0], {"vv_threshold_db": np.nan}, "thresholds must be finite"),
        ([1.0], [2.0], {"offsets_db": ()}, "at least one offset"),
        ([1.0], [2.0], {"offsets_db": (0.0, np.inf)}, "offsets_db values must be finite"),
        ([1.0], [2.0], {"valid_mask": [True, False]}, "same shape"),
    ],
)
def test_rejects_invalid_inputs(vv, vh, kwargs, message):
    parameters = {"vv_threshold_db": -12.0, "vh_threshold_db": -15.0}
    parameters.update(kwargs)
    with pytest.raises(ValueError, match=message):
        run_threshold_sensitivity(vv, vh, **parameters)
