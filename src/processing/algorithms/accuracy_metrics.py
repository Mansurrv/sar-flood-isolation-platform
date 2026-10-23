"""Accuracy and result-comparison metrics for flood masks."""

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass(frozen=True)
class AccuracyMetrics:
    """Binary confusion counts and derived evaluation metrics."""

    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int
    excluded_pixels: int
    iou: float
    precision: float
    recall: float
    f1: float
    cohen_kappa: float


@dataclass(frozen=True)
class IsolationComparison:
    """Pairwise set similarity and consensus/disputed settlement IDs."""

    jaccard: dict[tuple[str, str], float]
    consensus: tuple[str, ...]
    disputed: tuple[str, ...]


def evaluate_binary_mask(
    prediction: ArrayLike,
    reference: ArrayLike,
    *,
    valid_mask: ArrayLike | None = None,
) -> AccuracyMetrics:
    """Evaluate a prediction against a binary reference over common valid cells.

    Non-finite values are excluded. Undefined zero-denominator ratios are
    returned as 0. Cohen's kappa is defined as 1 for perfect agreement when
    expected agreement is exactly 1, and 0 for the other degenerate case.
    """
    predicted = np.asarray(prediction, dtype=np.float64)
    expected = np.asarray(reference, dtype=np.float64)
    if predicted.ndim == 0 or predicted.shape != expected.shape:
        raise ValueError("prediction and reference must have matching array shapes")

    valid = np.isfinite(predicted) & np.isfinite(expected)
    if valid_mask is not None:
        supplied_mask = np.asarray(valid_mask, dtype=np.bool_)
        if supplied_mask.shape != predicted.shape:
            raise ValueError("valid_mask must have the same shape as the masks")
        valid &= supplied_mask
    if not np.isin(predicted[valid], (0.0, 1.0)).all():
        raise ValueError("prediction must contain only binary values 0 and 1")
    if not np.isin(expected[valid], (0.0, 1.0)).all():
        raise ValueError("reference must contain only binary values 0 and 1")

    predicted_positive = predicted[valid] == 1
    expected_positive = expected[valid] == 1
    tp = int(np.count_nonzero(predicted_positive & expected_positive))
    fp = int(np.count_nonzero(predicted_positive & ~expected_positive))
    fn = int(np.count_nonzero(~predicted_positive & expected_positive))
    tn = int(np.count_nonzero(~predicted_positive & ~expected_positive))
    total = tp + fp + fn + tn

    iou = _ratio(tp, tp + fp + fn)
    precision = _ratio(tp, tp + fp)
    recall = _ratio(tp, tp + fn)
    f1 = _ratio(2 * tp, 2 * tp + fp + fn)
    if total == 0:
        kappa = 0.0
    else:
        observed_agreement = (tp + tn) / total
        expected_agreement = (
            ((tp + fp) * (tp + fn) + (fn + tn) * (fp + tn)) / total**2
        )
        denominator = 1.0 - expected_agreement
        if denominator == 0.0:
            kappa = 1.0 if observed_agreement == 1.0 else 0.0
        else:
            kappa = (observed_agreement - expected_agreement) / denominator

    return AccuracyMetrics(
        true_positive=tp,
        false_positive=fp,
        false_negative=fn,
        true_negative=tn,
        excluded_pixels=int(predicted.size - total),
        iou=iou,
        precision=precision,
        recall=recall,
        f1=f1,
        cohen_kappa=float(kappa),
    )


def compare_isolation_sets(
    isolation_sets: Mapping[str, set[str] | frozenset[str]],
) -> IsolationComparison:
    """Compare named isolation sets using Jaccard and consensus membership."""
    names = sorted(isolation_sets)
    normalized = {name: set(isolation_sets[name]) for name in names}
    pairwise: dict[tuple[str, str], float] = {}
    for first, second in combinations(names, 2):
        union = normalized[first] | normalized[second]
        intersection = normalized[first] & normalized[second]
        pairwise[(first, second)] = (
            1.0 if not union else len(intersection) / len(union)
        )

    if not names:
        return IsolationComparison(pairwise, (), ())
    all_ids = set.union(*(normalized[name] for name in names))
    common_ids = set.intersection(*(normalized[name] for name in names))
    return IsolationComparison(
        jaccard=pairwise,
        consensus=tuple(sorted(common_ids)),
        disputed=tuple(sorted(all_ids - common_ids)),
    )


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
