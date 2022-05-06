"""Compute and aggregate metrics over nodes, source code, files, and directories."""
import itertools
import typing

import astroid.nodes
import more_itertools

from sourcery_analytics.cli.data import ThresholdBreach
from sourcery_analytics.conditions import is_method
from sourcery_analytics.extractors import Extractable, extract
from sourcery_analytics.metrics import (
    standard_method_metrics,
)
from sourcery_analytics.metrics.aggregations import Aggregation
from sourcery_analytics.metrics.compounders import (
    name_metrics,
    Compounder,
    NamedMetricResult,
)
from sourcery_analytics.metrics.types import (
    Metric,
    MethodMetric,
    MetricResult,
)
from sourcery_analytics.metrics.utils import method_file, method_lineno, method_name
from sourcery_analytics.settings import ThresholdSettings

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
    metric: Metric[N, R] = compounder(*metrics)
    results = (metric(node) for node in nodes)
    return aggregation(results)


def melt(
    results: typing.Iterable[NamedMetricResult], metrics: typing.List[Metric[N, T]]
) -> typing.Iterator[typing.Dict[str, typing.Any]]:
    metric_vars = [m.__name__ for m in metrics]
    first_result, *remaining_results = results
    id_vars = [k for k in first_result.keys() if k not in metric_vars]
    yield from melt_one(first_result, metric_vars, id_vars)
    for result in remaining_results:
        yield from melt_one(result, metric_vars, id_vars)


def melt_one(
    result: NamedMetricResult, metric_vars: typing.List[str], id_vars: typing.List[str]
) -> typing.Iterator[typing.Dict[str, typing.Any]]:
    id_values = {id_var: result[id_var] for id_var in id_vars}
    for metric_var in metric_vars:
        metric_values = {"metric_name": metric_var, "metric_value": result[metric_var]}
        yield id_values | metric_values


def assess(
    nodes: typing.Union[N, typing.Iterable[N]],
    /,
    metrics: typing.Union[Metric[N, T], typing.Iterable[Metric[N, T]]] = None,
    threshold_settings: ThresholdSettings = ThresholdSettings(),
) -> typing.Iterator[NamedMetricResult]:
    nodes = more_itertools.always_iterable(nodes, base_type=astroid.nodes.NodeNG)
    metrics = list(more_itertools.always_iterable(metrics))
    threshold_values = threshold_settings.dict()
    metric: Metric[N, NamedMetricResult] = name_metrics(
        method_file, method_lineno, method_name, *metrics
    )
    results = melt((metric(node) for node in nodes), metrics)
    for result in results:
        metric_name = result["metric_name"].removeprefix("method_")
        metric_value = result["metric_value"]
        threshold_value = threshold_values[metric_name]
        if metric_value > threshold_value:
            yield result
