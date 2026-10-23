import pytest

from src.backend.app.gee_client import otsu_from_histogram


def test_otsu_from_two_class_histogram_returns_midpoint():
    threshold = otsu_from_histogram(
        {"histogram": [10, 10], "bucketMeans": [-20.0, -5.0]}
    )
    assert threshold == -12.5


@pytest.mark.parametrize(
    "histogram",
    [
        {},
        {"histogram": [], "bucketMeans": []},
        {"histogram": [1], "bucketMeans": [0]},
        {"histogram": [1, 1], "bucketMeans": [0]},
    ],
)
def test_otsu_rejects_histograms_without_a_valid_split(histogram):
    with pytest.raises(RuntimeError):
        otsu_from_histogram(histogram)


def test_otsu_rejects_zero_count_histogram():
    with pytest.raises(RuntimeError, match="empty histogram"):
        otsu_from_histogram(
            {"histogram": [0, 0], "bucketMeans": [-20.0, -5.0]}
        )
