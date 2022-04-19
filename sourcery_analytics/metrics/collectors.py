"""Functions for combining multiple metrics into single ones."""
import numbers
import typing

import astroid
from mypy_extensions import VarArg

from sourcery_analytics.metrics import Metric

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T")
U = typing.TypeVar("U")


Collector = typing.Callable[[VarArg(Metric[N, T])], Metric[N, U]]


def tuple_metrics(*metrics: Metric[N, T]) -> Metric[N, typing.Tuple[T, ...]]:
    """A collector which joins the results in a tuple."""

    def tupled_metrics(node: N) -> typing.Tuple[T, ...]:
        return TupledMetrics(metric(node) for metric in metrics)

    return tupled_metrics


def name_metrics(*metrics: Metric[N, T]) -> Metric[N, typing.Dict[str, T]]:
    """A collector which names the results via the metric names."""

    def name_dict(node: N) -> typing.Dict[str, T]:
        return NamedMetrics({metric.__name__: metric(node) for metric in metrics})

    return name_dict


class _CollectedMetrics:
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
        try:
            return v + u
        except TypeError:
            return None


class TupledMetrics(typing.Tuple[T], _CollectedMetrics):
    def __add__(self, other):
        return TupledMetrics((self.addone(v, u) for v, u in zip(self, other)))

    def __truediv__(self, other):
        return TupledMetrics((self.divone(v, other) for v in self))


class NamedMetrics(typing.Dict[str, T], _CollectedMetrics):
    def __add__(self, other):
        return NamedMetrics(
            {
                k: self.addone(self.get(k), other.get(k))
                for k in self.keys() | other.keys()
            }
        )

    def __truediv__(self, other):
        return NamedMetrics({k: self.divone(self.get(k), other) for k in self.keys()})

    def __iter__(self):
        return iter(self.items())
