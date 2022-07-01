"""Types and abstract base classes for metrics."""
import typing

import astroid


class MetricResult(typing.Protocol):
    """An value supporting aggregation."""

    def __add__(self, other):
        ...  # pragma: no cover

    def __truediv__(self, other):
        ...  # pragma: no cover


Metric = typing.Callable[[astroid.nodes.NodeNG], MetricResult]
IterMetric = typing.Callable[[typing.Iterable[astroid.nodes.NodeNG]], MetricResult]
MethodMetric = typing.Callable[[astroid.FunctionDef], MetricResult]
