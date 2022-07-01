"""Functions to combine the results from multiple nodes into a single result."""
import functools
import itertools
import operator
import typing

from sourcery_analytics.metrics.types import MetricResult

S_co = typing.TypeVar("S_co", covariant=True)


class Aggregation(typing.Protocol[S_co]):
    """Aggregates metric results into a single result."""

    def __call__(self, results: typing.Iterable[MetricResult], /) -> S_co:
        """Aggregates the metric results into a single result."""


def average(results: typing.Iterable[MetricResult]) -> MetricResult:
    """Returns the arithmetic average of the results."""
    total_iter, count_iter = itertools.tee(results)
    # sum doesn't use __add__, so use operator here instead
    total_ = total(total_iter)
    count = len(list(count_iter))
    return total_ / count


def total(results: typing.Iterable[MetricResult]) -> MetricResult:
    """Returns the arithmetic total of the results."""
    return functools.reduce(operator.add, results)


def peak(results: typing.Iterable[MetricResult]) -> MetricResult:
    """Returns the highest value out of the results.

    Note that for strings, this will return the value highest in alphabetical order.
    """
    first, *remainder = results
    # deconstruct each "row", get the max across each "column", and reconstruct
    # from the type of the first result
    return type(first)((max(r) for r in zip(*(first, *remainder))))  # type: ignore
