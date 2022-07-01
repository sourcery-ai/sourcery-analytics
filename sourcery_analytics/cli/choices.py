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

    COGNITIVE_COMPLEXITY = "cognitive_complexity"
    CYCLOMATIC_COMPLEXITY = "cyclomatic_complexity"
    LENGTH = "length"
    WORKING_MEMORY = "working_memory"

    @property
    def method_method_name(self):
        """Returns the method metric's actual function name, used for sorting."""
        return f"method_{self.value}"

    def as_method_metric(self) -> MethodMetric:
        """Returns the string choice as a callable method."""
        return {
            MethodMetricChoice.COGNITIVE_COMPLEXITY: method_cognitive_complexity,
            MethodMetricChoice.CYCLOMATIC_COMPLEXITY: method_cyclomatic_complexity,
            MethodMetricChoice.LENGTH: method_length,
            MethodMetricChoice.WORKING_MEMORY: method_working_memory,
        }[self]


class AggregationChoice(enum.Enum):
    """Aggregations available to the CLI."""

    TOTAL = "total"
    AVERAGE = "average"
    PEAK = "peak"

    def as_aggregation(self) -> Aggregation:
        """Returns the string choice as a callable method."""
        return {
            AggregationChoice.TOTAL: total,
            AggregationChoice.AVERAGE: average,
            AggregationChoice.PEAK: peak,
        }[self]


class OutputChoice(enum.Enum):
    """Outputs available in the CLI."""

    PLAIN = "plain"
    RICH = "rich"
    CSV = "csv"
