import pytest

from sourcery_analytics.metrics import statement_count
from sourcery_analytics.metrics.compounders import (
    tuple_metrics,
    TupleMetricResult,
    name_metrics,
    NamedMetricResult,
)
from sourcery_analytics.metrics.method_length import total_statement_count


@pytest.fixture
def source():
    return """
        def sub(x, y):
            return x - y
    """


def test_tuple_metrics(node):
    metric = tuple_metrics(statement_count, total_statement_count)
    result = metric(node)
    assert result == TupleMetricResult((0, 1))


def test_name_metrics(node):
    metric = name_metrics(statement_count, total_statement_count)
    result = metric(node)
    assert result == NamedMetricResult(
        {"statement_count": 0, "total_statement_count": 1}
    )
