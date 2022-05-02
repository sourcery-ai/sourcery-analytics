"""Choices, implemented as Enums, associated with the CLI."""

import enum

from sourcery_analytics.metrics import (
    method_cognitive_complexity,
    method_cyclomatic_complexity,
    method_length,
    method_working_memory,
)
from sourcery_analytics.metrics.aggregations import Aggregation, total, average, peak
from sourcery_analytics.metrics.types import MethodMetric


class MethodMetricChoice(enum.Enum):
    """Method metrics available to the CLI."""

    cognitive_complexity = "cognitive_complexity"
    cyclomatic_complexity = "cyclomatic_complexity"
    length = "length"
    working_memory = "working_memory"

    @property
    def method_method_name(self):
        """Returns the method metric's actual function name, used for sorting."""
        return f"method_{self.value}"

    def as_method_metric(self) -> MethodMetric:
        """Returns the string choice as a callable method."""
        return {
            MethodMetricChoice.cognitive_complexity: method_cognitive_complexity,
            MethodMetricChoice.cyclomatic_complexity: method_cyclomatic_complexity,
            MethodMetricChoice.length: method_length,
            MethodMetricChoice.working_memory: method_working_memory,
        }[self]


class AggregationChoice(enum.Enum):
    """Aggregations available to the CLI."""

    total = "total"
    average = "average"
    peak = "peak"

    def as_aggregation(self) -> Aggregation:
        """Returns the string choice as a callable method."""
        return {
            AggregationChoice.total: total,  # type: ignore
            AggregationChoice.average: average,
            AggregationChoice.peak: peak,
        }[self]


class OutputChoice(enum.Enum):
    """Outputs available in the CLI."""

    plain = "plain"
    rich = "rich"
    csv = "csv"
