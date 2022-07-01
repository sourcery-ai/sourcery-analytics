"""Functions for creating compound metrics."""
import typing

import astroid.nodes

from sourcery_analytics.metrics.types import Metric, MetricResult


class Compounder(typing.Protocol):
    """A compounder function produces a compound metric function."""

    def __call__(self, *metrics: Metric) -> Metric:
        """Combine multiple metric functions into a single metric function."""


def tuple_metrics(*metrics: Metric) -> "TupleMetric":
    """A compounder which joins the results in a tuple."""

    def tupled_metrics(node: astroid.nodes.NodeNG) -> "TupleMetricResult":
        return TupleMetricResult(metric(node) for metric in metrics)

    return tupled_metrics


def name_metrics(*metrics: Metric) -> "NamedMetric":
    """A compounder which joins the result as a dictionary keyed on the metric names."""

    def name_dict(node: astroid.nodes.NodeNG) -> "NamedMetricResult":
        return NamedMetricResult({metric.__name__: metric(node) for metric in metrics})

    return name_dict


class _CompoundMetricResult:
    @staticmethod
    def _divone(numerator, denominator):
        try:
            return numerator / denominator
        except (TypeError, ZeroDivisionError):
            return None

    @staticmethod
    def _addone(augend, addend):
        if not isinstance(augend, (float, int)) or not isinstance(addend, (float, int)):
            return None
        return augend + addend

    @staticmethod
    def _eqone(left, right):
        return left == right


class TupleMetricResult(typing.Tuple[MetricResult, ...], _CompoundMetricResult):
    """A compound metric result comprising a tuple of sub-result values."""

    def __add__(self, other):
        return TupleMetricResult((self._addone(v, u) for v, u in zip(self, other)))

    def __truediv__(self, other):
        return TupleMetricResult((self._divone(v, other) for v in self))

    def __eq__(self, other):
        return all(self._eqone(v, u) for v, u in zip(self, other))


class NamedMetricResult(typing.Dict[str, MetricResult], _CompoundMetricResult):
    """A compound metric result mapping sub-metric name to sub-metric result."""

    def __add__(self, other):
        return NamedMetricResult(
            {k: self._addone(self.get(k), other.get(k)) for k in self.keys()}
        )

    def __truediv__(self, other):
        return NamedMetricResult(
            {k: self._divone(self.get(k), other) for k in self.keys()}
        )

    def __iter__(self):
        return iter(self.items())

    def __eq__(self, other):
        return all(self._eqone(u, other[k]) for k, u in self.items())


TupleMetric = typing.Callable[[astroid.nodes.NodeNG], TupleMetricResult]
NamedMetric = typing.Callable[[astroid.nodes.NodeNG], NamedMetricResult]
