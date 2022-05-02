"""Types and abstract base classes for metrics."""
from __future__ import annotations

import typing

import astroid


class MetricResult(typing.Protocol):
    """An value supporting aggregation."""

    def __add__(self, other):
        ...  # pragma: no cover

    def __truediv__(self, other):
        ...  # pragma: no cover


N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
R = typing.TypeVar("R", bound=MetricResult)
Metric = typing.Callable[[N], R]
IterMetric = typing.Callable[[typing.Iterable[N]], R]
MethodMetric = typing.Callable[[astroid.FunctionDef], R]
