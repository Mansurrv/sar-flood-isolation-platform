import numpy as np
import pytest

from src.processing.algorithms.baseline_change import baseline_change_detection


def test_classifies_new_darkening_but_not_persistent_dark_surfaces():
    pre = np.array([[-10.0, -20.0, -10.0, -10.0]])
    post = np.array([[-20.0, -21.0, -12.0, -20.0]])

    result = baseline_change_detection(pre, post)

    assert result.flood_mask.tolist() == [[True, False, False, True]]
    assert result.change_db.tolist() == [[-10.0, -1.0, -2.0, -10.0]]


def test_applies_strict_threshold_and_post_flood_cap():
    result = baseline_change_detection(
        [-10.0, -10.0],
        [-13.0, -20.0],
        change_threshold_db=-3.0,
        post_flood_cap_db=-15.0,
    )

    assert result.flood_mask.tolist() == [False, True]


def test_masks_nonfinite_and_explicitly_invalid_pixels():
    pre = np.array([[-10.0, np.nan], [-10.0, -10.0]])
    post = np.array([[-20.0, -20.0], [-20.0, -20.0]])
    valid = np.array([[True, True], [False, True]])

    result = baseline_change_detection(pre, post, valid_mask=valid)

    assert result.valid_mask.tolist() == [[True, False], [False, True]]
    assert result.flood_mask.tolist() == [[True, False], [False, True]]
    assert np.isnan(result.change_db[0, 1])


@pytest.mark.parametrize(
    ("pre", "post", "kwargs", "message"),
    [
        ([1.0], [[1.0]], {}, "matching array shapes"),
        ([1.0], [2.0], {"change_threshold_db": np.inf}, "must be finite"),
        ([1.0], [2.0], {"valid_mask": [True, False]}, "same shape"),
    ],
)
def test_rejects_invalid_inputs(pre, post, kwargs, message):
    with pytest.raises(ValueError, match=message):
        baseline_change_detection(pre, post, **kwargs)
