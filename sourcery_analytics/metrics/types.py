"""Types and abstract base classes for metrics."""
from __future__ import annotations

import abc
import typing

import astroid

from sourcery_analytics.visitors import Visitor


class MetricResult(typing.Protocol):
    """An value supporting aggregation."""

    def __add__(self, other):
        ...

    def __truediv__(self, other):
        ...

    def __lt__(self, other):
        ...


N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
R = typing.TypeVar("R", bound=MetricResult)
Metric = typing.Callable[[N], R]
IterMetric = typing.Callable[[typing.Iterable[N]], R]
MethodMetric = typing.Callable[[astroid.FunctionDef], R]


class MetricVisitor(Visitor[R]):
    """A visitor which returns a :py:class:`.MetricResult`, suitable for aggregation."""

    @property
    @abc.abstractmethod
    def __name__(self) -> str:
        ...
