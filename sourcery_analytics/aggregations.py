"""Calculations over collections of numeric metric results."""
import functools
import itertools
import operator
import typing

import astroid

from sourcery_analytics.metrics import Metric, MetricResult

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
R = typing.TypeVar("R", bound=MetricResult)
U = typing.TypeVar("U")
Aggregation = typing.Callable[[typing.Iterable[N]], R]
MetricAggregation = typing.Callable[[Metric[N, R]], Aggregation[N, U]]


def average(metric: Metric[N, R]) -> Aggregation[N, R]:
    """Returns the arithmetic mean of the inputs."""

    def over(nodes: typing.Iterable[N]) -> R:
        return _mean((metric(node) for node in nodes))

    return over


def total(metric: Metric[N, R]) -> Aggregation[N, R]:
    """Returns the arithmetic total of the inputs."""

    def over(nodes: typing.Iterable[N]) -> R:
        return functools.reduce(operator.add, (metric(node) for node in nodes))

    return over


def peak(metric: Metric[N, R]) -> Aggregation[N, typing.List[R]]:
    """Returns the highest value of the inputs.

    Note that for strings, this will return the
    """

    def over(nodes: typing.Iterable[N]) -> typing.List[R]:
        first, *remainder = (metric(node) for node in nodes)
        return type(first)((max(r) for r in zip(*(first, *remainder))))

    return over


def collect(metric: Metric[N, R]) -> Aggregation[N, typing.List[R]]:
    def over(nodes: typing.Iterable[N]) -> typing.List[R]:
        return [metric(node) for node in nodes]

    return over


def _mean(xs: typing.Iterable[R], /) -> R:
    total_iter, count_iter = itertools.tee(xs)
    total_ = functools.reduce(operator.add, total_iter)
    count = len(list(count_iter))
    return total_ / count
