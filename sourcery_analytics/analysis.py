"""Compute and aggregate metrics over nodes, source code, files, and directories."""
import typing

import astroid.nodes
import more_itertools

from sourcery_analytics.conditions import is_method
from sourcery_analytics.extractors import Extractable, extract
from sourcery_analytics.metrics import (
    standard_method_metrics,
)
from sourcery_analytics.metrics.aggregations import Aggregation
from sourcery_analytics.metrics.compounders import name_metrics, Compounder
from sourcery_analytics.metrics.types import (
    Metric,
    MethodMetric,
    MetricResult,
)

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T", bound=MetricResult)
R = typing.TypeVar("R", bound=MetricResult)


def analyze_methods(
    item: Extractable,
    /,
    metrics: typing.Union[
        None, MethodMetric[T], typing.Iterable[MethodMetric[T]]
    ] = None,
    compounder: Compounder[astroid.nodes.FunctionDef, T, R] = name_metrics,  # type: ignore
    aggregation: Aggregation[R] = list,  # type: ignore
) -> R:
    """Extracts methods from ``item`` then computes and aggregates metrics.

    Args:
        item: source code, node, file path, or directory path to analyze
        metrics: list of node metrics to compute
        compounder: method to combine individual metrics into compound metric
        aggregation: method to combine the results

    Examples:
        >>> from sourcery_analytics.metrics import (
        ...     method_name,
        ...     method_cognitive_complexity,
        ... )
        >>> source = '''
        ...     def foo():
        ...         return False
        ...     def bar():
        ...         if foo():
        ...             return False
        ...         return True
        ... '''
        >>> analyze_methods(
        ...     source,
        ...     metrics=(method_name, method_cognitive_complexity)
        ... )
        [{'method_name': 'foo', 'method_cognitive_complexity': 0}, {'method_name': 'bar', 'method_cognitive_complexity': 1}]
        >>> from sourcery_analytics.metrics.aggregations import average
        >>> sorted(analyze_methods(
        ...     source,
        ...     metrics=(method_name, method_cognitive_complexity),
        ...     aggregation=average
        ... ))
        [('method_cognitive_complexity', 0.5), ('method_name', None)]
    """
    methods: typing.Iterator[astroid.nodes.FunctionDef] = extract(
        item, condition=is_method
    )
    if not metrics:
        metrics = standard_method_metrics()
    return analyze(
        methods, metrics=metrics, compounder=compounder, aggregation=aggregation
    )


def analyze(
    nodes: typing.Union[N, typing.Iterable[N]],
    /,
    metrics: typing.Union[Metric[N, T], typing.Iterable[Metric[N, T]]] = None,
    compounder: Compounder[N, T, R] = name_metrics,  # type: ignore
    aggregation: Aggregation[R] = list,  # type: ignore
) -> R:
    """Computes and aggregates metrics over ``nodes``.

    Examples:
        >>> from sourcery_analytics.metrics import (
        ...     method_name,
        ...     method_cognitive_complexity,
        ...     method_cyclomatic_complexity,
        ... )
        >>> source = '''
        ...     def add(x, y): #@
        ...         return x + y
        ...
        ...     def div(x, y): #@
        ...         return None if y == 0 else x / y
        ... '''
        >>> methods = astroid.extract_node(source)
        >>> analyze(methods, metrics=(method_name, method_cognitive_complexity, method_cyclomatic_complexity))
        [{'method_name': 'add', 'method_cognitive_complexity': 0, 'method_cyclomatic_complexity': 0}, {'method_name': 'div', 'method_cognitive_complexity': 2, 'method_cyclomatic_complexity': 2}]
    """
    nodes = more_itertools.always_iterable(nodes, base_type=astroid.nodes.NodeNG)
    metrics = more_itertools.always_iterable(metrics)
    metric = compounder(*metrics)
    results = (metric(node) for node in nodes)
    return aggregation(results)
