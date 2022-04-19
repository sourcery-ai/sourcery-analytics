import pytest

from sourcery_analytics.aggregations import _mean


@pytest.mark.parametrize(
    "xs, expected",
    [
        ([1, 2, 3], 2.0),
        (iter([1, 2, 3]), 2.0),
    ],
)
def test_mean(xs, expected):
    assert _mean(xs) == expected
