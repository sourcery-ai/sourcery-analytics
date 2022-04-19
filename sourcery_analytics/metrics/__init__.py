"""Static code quality metrics, computed from astroid nodes."""
from __future__ import annotations

import typing

import astroid

from sourcery_analytics.metrics.cognitive_complexity import method_cognitive_complexity
from sourcery_analytics.metrics.cyclomatic_complexity import (
    method_cyclomatic_complexity,
)
from sourcery_analytics.metrics.method_length import method_length
from sourcery_analytics.metrics.working_memory import method_working_memory
from sourcery_analytics.metrics.utils import method_qualname, method_name


class MetricResult(typing.Protocol):
    def __add__(self, other):
        ...

    def __truediv__(self, other):
        ...

    def __lt__(self, other):
        ...


N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
R = typing.TypeVar("R", bound=MetricResult)

Metric = typing.Callable[[N], R]
MethodMetric = typing.Callable[[astroid.FunctionDef], R]
