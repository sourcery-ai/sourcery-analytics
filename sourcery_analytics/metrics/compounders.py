"""Functions for creating compound metrics."""
import typing

import astroid

from sourcery_analytics.metrics.types import Metric

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T", contravariant=True)
U = typing.TypeVar("U")


class Compounder(typing.Protocol[N, T, U]):
    """A compounder function produces a compound metric function."""

    def __call__(self, *metrics: Metric[N, T]) -> Metric[N, U]:
        """Combine multiple metric functions into a single metric function."""


def tuple_metrics(*metrics: Metric[N, T]) -> Metric[N, typing.Tuple[T, ...]]:
    """A compounder which joins the results in a tuple."""

    def tupled_metrics(node: N) -> typing.Tuple[T, ...]:
        return TupleMetricResult(metric(node) for metric in metrics)

    return tupled_metrics


def name_metrics(*metrics: Metric[N, T]) -> Metric[N, "NamedMetricResult"]:
    """A compounder which joins the result via a dictionary keyed on the metric names."""

    def name_dict(node: N) -> NamedMetricResult:
        return NamedMetricResult({metric.__name__: metric(node) for metric in metrics})

    return name_dict


class _CompoundMetricResult:
    @staticmethod
    def divone(v, u):
        try:
            return v / u
        except (TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def addone(v, u):
        if not isinstance(v, (float, int)) or not isinstance(u, (float, int)):
            return None
        return v + u

    @staticmethod
    def eqone(v, u):
        return v == u


class TupleMetricResult(typing.Tuple[T], _CompoundMetricResult):
    """A compound metric result comprising a tuple of sub-result values."""

    def __add__(self, other):
        return TupleMetricResult((self.addone(v, u) for v, u in zip(self, other)))

    def __truediv__(self, other):
        return TupleMetricResult((self.divone(v, other) for v in self))

    def __eq__(self, other):
        return all(self.eqone(v, u) for v, u in zip(self, other))


class NamedMetricResult(typing.Dict[str, T], _CompoundMetricResult):
    """A compound metric result mapping sub-metric name to sub-metric result."""

    def __add__(self, other):
        return NamedMetricResult(
            {k: self.addone(self.get(k), other.get(k)) for k in self.keys()}
        )

    def __truediv__(self, other):
        return NamedMetricResult(
            {k: self.divone(self.get(k), other) for k in self.keys()}
        )

    def __iter__(self):
        return iter(self.items())

    def __eq__(self, other):
        return all(self.eqone(self[k], other[k]) for k in self.keys())
