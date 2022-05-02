"""Static code quality metrics, computed from astroid nodes.

A Metric is a function over a node that returns a MetricResult, which must be
orderable (to compute max values), addable (to compute totals) and dividable (to
compute averages). Numbers, therefore, always count, and the results of multiple
metrics can be combined into a compound metric result that fulfils these requirements.

This module also defines a MethodMetric, which is a metric specifically for methods
(function definitions).
"""
from __future__ import annotations

from sourcery_analytics.metrics.cognitive_complexity import (
    method_cognitive_complexity,
    CognitiveComplexityVisitor,
)
from sourcery_analytics.metrics.cyclomatic_complexity import (
    method_cyclomatic_complexity,
    cyclomatic_complexity,
)
from sourcery_analytics.metrics.method_length import method_length, statement_count
from sourcery_analytics.metrics.utils import (
    method_qualname,
    method_name,
    node_type_name,
)
from sourcery_analytics.metrics.working_memory import (
    method_working_memory,
    WorkingMemoryVisitor,
)


def standard_method_metrics():
    """Returns a collection of standard metrics to be used on methods."""
    return (
        method_qualname,
        method_length,
        method_cyclomatic_complexity,
        method_cognitive_complexity,
        method_working_memory,
    )
