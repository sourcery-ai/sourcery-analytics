import enum

from sourcery_analytics.aggregations import (
    MetricAggregation,
    average,
    total,
    collect,
    peak,
)
from sourcery_analytics.metrics import (
    MethodMetric,
    method_cognitive_complexity,
    method_cyclomatic_complexity,
    method_length,
    method_working_memory,
)
from sourcery_analytics.metrics.collectors import Collector, tuple_metrics, name_metrics
from sourcery_analytics.metrics.utils import method_itself, method_qualname


class MethodMetricChoice(enum.Enum):
    """Method metrics available to the CLI."""

    cognitive_complexity = "cognitive_complexity"
    cyclomatic_complexity = "cyclomatic_complexity"
    length = "length"
    working_memory = "working_memory"
    qualname = "qualname"
    itself = "itself"

    def as_callable(self) -> MethodMetric:
        return {
            MethodMetricChoice.cognitive_complexity: method_cognitive_complexity,
            MethodMetricChoice.cyclomatic_complexity: method_cyclomatic_complexity,
            MethodMetricChoice.length: method_length,
            MethodMetricChoice.working_memory: method_working_memory,
            MethodMetricChoice.qualname: method_qualname,
            MethodMetricChoice.itself: method_itself,
        }[self]


class CollectorChoice(enum.Enum):
    tuple = "tuple"
    name = "name"

    def as_callable(self) -> Collector:
        return {
            CollectorChoice.tuple: tuple_metrics,
            CollectorChoice.name: name_metrics,
        }[self]


class AggregationChoice(enum.Enum):
    """Aggregations available to the CLI."""

    total = "total"
    average = "average"
    collect = "list"
    peak = "peak"

    def as_callable(self) -> MetricAggregation:
        """Returns the string choice as a callable method."""
        return {
            AggregationChoice.total: total,  # type: ignore
            AggregationChoice.average: average,
            AggregationChoice.collect: collect,
            AggregationChoice.peak: peak,
        }[self]


class OutputChoice(enum.Enum):
    plain = "plain"
    rich = "rich"
