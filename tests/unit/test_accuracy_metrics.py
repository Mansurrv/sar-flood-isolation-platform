import numpy as np
import pytest

from src.processing.algorithms.accuracy_metrics import (
    compare_isolation_sets,
    evaluate_binary_mask,
)


def test_hand_computed_confusion_metrics():
    result = evaluate_binary_mask(
        [[1, 1], [0, 0]],
        [[1, 0], [1, 0]],
    )

    assert (result.true_positive, result.false_positive) == (1, 1)
    assert (result.false_negative, result.true_negative) == (1, 1)
    assert result.excluded_pixels == 0
    assert result.iou == pytest.approx(1 / 3, abs=1e-4)
    assert result.precision == pytest.approx(0.5, abs=1e-4)
    assert result.recall == pytest.approx(0.5, abs=1e-4)
    assert result.f1 == pytest.approx(0.5, abs=1e-4)
    assert result.cohen_kappa == pytest.approx(0.0, abs=1e-4)


def test_perfect_and_completely_wrong_maps():
    perfect = evaluate_binary_mask([1, 0, 1, 0], [1, 0, 1, 0])
    wrong = evaluate_binary_mask([1, 1, 0, 0], [0, 0, 1, 1])

    assert (perfect.iou, perfect.f1, perfect.cohen_kappa) == (1.0, 1.0, 1.0)
    assert (wrong.iou, wrong.f1, wrong.cohen_kappa) == (0.0, 0.0, -1.0)


def test_excludes_nodata_and_explicitly_masked_pixels():
    prediction = np.array([[1, 0], [1, np.nan]])
    reference = np.array([[1, 1], [0, 0]])
    valid = np.array([[True, True], [False, True]])

    result = evaluate_binary_mask(prediction, reference, valid_mask=valid)

    assert (result.true_positive, result.false_positive) == (1, 0)
    assert result.false_negative == 1
    assert result.excluded_pixels == 2
    assert result.iou == 0.5


def test_empty_and_degenerate_inputs_return_finite_defined_values():
    empty = evaluate_binary_mask([np.nan, np.nan], [0, 1])
    all_negative = evaluate_binary_mask([0, 0], [0, 0])

    assert empty.excluded_pixels == 2
    assert empty.cohen_kappa == 0.0
    assert all_negative.iou == 0.0
    assert all_negative.cohen_kappa == 1.0
    assert all(
        np.isfinite(value)
        for value in (
            empty.iou,
            empty.precision,
            empty.recall,
            empty.f1,
            empty.cohen_kappa,
        )
    )


@pytest.mark.parametrize(
    ("prediction", "reference", "kwargs", "message"),
    [
        ([1], [[1]], {}, "matching array shapes"),
        ([0, 2], [0, 1], {}, "binary values"),
        ([0, 1], [0, 2], {}, "binary values"),
        ([0, 1], [0, 1], {"valid_mask": [True]}, "same shape"),
    ],
)
def test_rejects_invalid_masks(prediction, reference, kwargs, message):
    with pytest.raises(ValueError, match=message):
        evaluate_binary_mask(prediction, reference, **kwargs)


def test_compares_isolation_sets_with_jaccard_consensus_and_disputed_ids():
    result = compare_isolation_sets(
        {
            "otsu": {"a", "b"},
            "local": {"b", "c"},
            "baseline": {"b", "d"},
        }
    )

    assert result.jaccard[("local", "otsu")] == pytest.approx(1 / 3)
    assert result.consensus == ("b",)
    assert result.disputed == ("a", "c", "d")


def test_empty_and_single_isolation_sets_are_supported():
    empty = compare_isolation_sets({})
    single = compare_isolation_sets({"method": set()})
    same_empty = compare_isolation_sets({"a": set(), "b": set()})

    assert empty.consensus == empty.disputed == ()
    assert single.consensus == single.disputed == ()
    assert same_empty.jaccard[("a", "b")] == 1.0
