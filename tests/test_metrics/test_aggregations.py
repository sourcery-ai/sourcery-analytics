import pytest

from sourcery_analytics.metrics.aggregations import average, total, peak
from sourcery_analytics.metrics.compounders import TupleMetricResult, NamedMetricResult


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ((1, 2, 3), 2),
        (iter([1, 2, 3]), 2),
        ([TupleMetricResult((1,)), TupleMetricResult((2,))], TupleMetricResult((1.5,))),
        (
            [NamedMetricResult({"x": 1}), NamedMetricResult({"x": 2})],
            NamedMetricResult({"x": 1.5}),
        ),
    ],
)
def test_average(inputs, expected):
    result = average(inputs)
    assert result == expected


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ((1, 2, 3), 6),
        (iter([1, 2, 3]), 6),
        ([TupleMetricResult((1,)), TupleMetricResult((2,))], TupleMetricResult((3,))),
        (
            [NamedMetricResult({"x": 1}), NamedMetricResult({"x": 2})],
            NamedMetricResult({"x": 3}),
        ),
    ],
)
def test_total(inputs, expected):
    result = total(inputs)
    assert result == expected


@pytest.mark.parametrize(
    "inputs, expected",
    [
        ([TupleMetricResult((1,)), TupleMetricResult((2,))], TupleMetricResult((2,))),
        (
            [NamedMetricResult({"x": 1}), NamedMetricResult({"x": 2})],
            NamedMetricResult({"x": 2}),
        ),
    ],
)
def test_peak(inputs, expected):
    result = peak(inputs)
    assert result == expected
