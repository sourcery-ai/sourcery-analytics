"""Compute and aggregate metrics over methods, source code, files, and directories."""
import dataclasses
import typing

import astroid

from sourcery_analytics.aggregations import MetricAggregation, collect
from sourcery_analytics.cli import (
    MethodMetricChoice,
    AggregationChoice,
    CollectorChoice,
)
from sourcery_analytics.metrics import (
    MethodMetric,
    Metric,
    MetricResult,
)
from sourcery_analytics.metrics.collectors import name_metrics, Collector

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T", bound=MetricResult)
R = typing.TypeVar("R", bound=MetricResult)
U = typing.TypeVar("U")


@dataclasses.dataclass
class Analyzer(typing.Generic[N, T, U]):
    """Computer for method metrics.

    Examples:
        >>> from sourcery_analytics.metrics import (
        ...     method_name,
        ...     method_cognitive_complexity,
        ...     method_cyclomatic_complexity,
        ... )
        >>> source = '''
        ...     def add(x, y): #@
        ...         return x + y
        ...
        ...     def div(x, y): #@
        ...         return None if y == 0 else x / y
        ... '''
        >>> methods = astroid.extract_node(source)
        >>> analyzer = Analyzer.from_metrics(
        ...     method_name,
        ...     method_cognitive_complexity,
        ...     method_cyclomatic_complexity,
        ... )
        >>> analyzer.analyze(methods)
        [{'method_name': 'add', 'method_cognitive_complexity': 0, 'method_cyclomatic_complexity': 0}, {'method_name': 'div', 'method_cognitive_complexity': 2, 'method_cyclomatic_complexity': 2}]
    """

    metric: Metric[N, T]
    aggregation: MetricAggregation[N, T, U] = collect  # type: ignore

    def analyze(self, nodes: typing.Iterable[N]) -> U:
        """Aggregates the metric over the nodes."""
        return self.aggregation(self.metric)(nodes)

    @classmethod
    def from_metrics(
        cls,
        *metrics: Metric[N, R],
        collector: Collector[N, R, T] = name_metrics,  # type: ignore
        aggregation: MetricAggregation[N, T, U] = collect,  # type: ignore
    ) -> "Analyzer[N, T, U]":
        """Construct an analyzer from the metrics."""
        metric = collector(*metrics)
        return cls(metric, aggregation)  # type: ignore

    @classmethod
    def from_choices(
        cls,
        *method_metric_choices: MethodMetricChoice,
        collector_choice: CollectorChoice,
        aggregation_choice: AggregationChoice,
    ) -> "Analyzer":
        """Construct a method analyzer from the method metric choice and aggregation choice."""
        method_metrics = (
            method_metric_choice.as_callable()
            for method_metric_choice in method_metric_choices
        )
        return cls.from_metrics(
            *method_metrics,
            collector=collector_choice.as_callable(),
            aggregation=aggregation_choice.as_callable(),
        )
