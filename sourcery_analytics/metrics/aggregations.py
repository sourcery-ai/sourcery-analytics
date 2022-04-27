"""Functions to combine the results from multiple nodes into a single result."""
import functools
import itertools
import operator
import typing

import astroid.nodes

from sourcery_analytics.metrics.types import MetricResult

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
R = typing.TypeVar("R", bound=MetricResult)
Aggregation = typing.Callable[[typing.Iterable[R]], R]


def average(results: typing.Iterable[R]) -> R:
    """Returns the arithmetic average of the results."""
    total_iter, count_iter = itertools.tee(results)
    # sum doesn't use __add__, so use operator here instead
    total_ = total(total_iter)
    count = len(list(count_iter))
    return total_ / count


def total(results: typing.Iterable[R]) -> R:
    """Returns the arithmetic total of the results."""
    return functools.reduce(operator.add, results)


def peak(results: typing.Iterable[R]) -> R:
    """Returns the highest value out of the results.

    Note that for strings, this will return the value highest in alphabetical order.
    """
    first, *remainder = results
    # deconstruct each "row", get the max across each "column", and reconstruct
    # from the type of the first result
    return type(first)((max(r) for r in zip(*(first, *remainder))))  # type: ignore
