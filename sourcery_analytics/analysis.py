"""Compute and aggregate metrics over nodes, source code, files, and directories."""
import sys
import typing

import astroid.nodes
import more_itertools

from sourcery_analytics.cli.data import ThresholdBreachDict
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
    NamedMetric,
)
from sourcery_analytics.metrics.types import Metric, MethodMetric, MetricResult
from sourcery_analytics.metrics.utils import method_file, method_lineno, method_name
from sourcery_analytics.settings import ThresholdSettings


R = typing.TypeVar("R", bound=MetricResult)
S = typing.TypeVar("S", bound=MetricResult)
T = typing.TypeVar("T")


def analyze_methods(
    item: Extractable,
    /,
    metrics: typing.Union[MethodMetric, typing.Iterable[MethodMetric]] = None,
    compounder: Compounder = name_metrics,
    aggregation: Aggregation[T] = list,
) -> T:
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
        [{'method_name': 'foo', 'method_cognitive_complexity': 0}, {'method_name': ...
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
    nodes: typing.Union[astroid.nodes.NodeNG, typing.Iterable[astroid.nodes.NodeNG]],
    /,
    metrics: typing.Union[Metric, typing.Iterable[Metric]] = None,
    compounder: Compounder = name_metrics,  # type: ignore
    aggregation: Aggregation[T] = list,
) -> T:
    """Computes and aggregates metrics over ``nodes``.

    Examples:
        >>> from pprint import pprint
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
        >>> pprint(
        ...     analyze(
        ...         methods,
        ...         metrics=(
        ...             method_name,
        ...             method_cognitive_complexity,
        ...             method_cyclomatic_complexity
        ...         )
        ...     )
        ... )
        [{'method_cognitive_complexity': 0,
          'method_cyclomatic_complexity': 0,
          'method_name': 'add'},
         {'method_cognitive_complexity': 2,
          'method_cyclomatic_complexity': 2,
          'method_name': 'div'}]
    """
    nodes = more_itertools.always_iterable(nodes, base_type=astroid.nodes.NodeNG)
    metrics = more_itertools.always_iterable(metrics)
    metric = compounder(*metrics)
    results = (metric(node) for node in nodes)
    return aggregation(results)


def assess(
    nodes: typing.Union[astroid.nodes.NodeNG, typing.Iterable[astroid.nodes.NodeNG]],
    /,
    metrics: typing.Union[Metric, typing.Iterable[Metric]] = None,
    threshold_settings: ThresholdSettings = ThresholdSettings(),
) -> typing.Iterator[ThresholdBreachDict]:
    """Yields the nodes which breach the thresholds according to the metrics.

    Args:
        nodes: an iterable of nodes, compatible with the metrics
        metrics: a collection of metrics, which may have thresholds in the settings
        threshold_settings: describes the maximum allowed value for the metrics

    Examples:
        >>> from pprint import pprint
        >>> from sourcery_analytics.metrics import (
        ...     method_length,
        ...     method_cyclomatic_complexity
        ... )
        >>> source = '''
        ...     def bin(xs):
        ...         for x in xs:
        ...             if x < 8:
        ...                 yield "small"
        ...             elif x < 10:
        ...                 yield "medium"
        ...             elif x < 12:
        ...                 yield "large"
        ...             else:
        ...                 yield "extra large"
        ...     def call(f, *args, **kwargs):
        ...         return f(*args, **kwargs)
        ... '''
        >>> nodes = extract(source, is_method)
        >>> metrics = [method_length, method_cyclomatic_complexity]
        >>> threshold_settings = ThresholdSettings(method_cyclomatic_complexity=2)
        >>> # note: the above value is unreasonably low
        >>> pprint(
        ...     list(
        ...         assess(
        ...             nodes,
        ...             metrics=metrics,
        ...             threshold_settings=threshold_settings
        ...         )
        ...     )
        ... )
        [{'method_file': '<?>',
          'method_lineno': 1,
          'method_name': 'bin',
          'metric_name': 'method_cyclomatic_complexity',
          'metric_value': 5}]
    """
    nodes = more_itertools.always_iterable(nodes, base_type=astroid.nodes.NodeNG)
    metrics = list(more_itertools.always_iterable(metrics))
    threshold_values = threshold_settings.dict()
    metric: NamedMetric = name_metrics(
        method_file, method_lineno, method_name, *metrics
    )
    results = melt((metric(node) for node in nodes), metrics)
    for result in results:
        metric_value = result["metric_value"]
        threshold_value = threshold_values.get(result["metric_name"], sys.maxsize)
        if metric_value > threshold_value:
            yield result


def melt(
    results: typing.Iterable[NamedMetricResult],
    metrics: typing.List[Metric],
) -> typing.Iterator[ThresholdBreachDict]:
    """Converts "wide-form" analysis into "long-form" analysis.

    For each named metric, of the form {metric_name: metric_value, ...},
    create a new dictionary {"metric_name": metric_name, "metric_value": metric_value}.
    Keys in the analysis (such as method name) that are not metrics are left unchanged.

    Inspired by the functionality of pandas' `.melt()` method.

    Args:
        results: an iterable of named metric results, typically the output of a call to
            :py:func:`.analyze`
        metrics: a list of metric functions - should match the names used in the
            analysis

    Examples:
        >>> from pprint import pprint
        >>> from sourcery_analytics.metrics import (
        ...     method_length,
        ...     method_cyclomatic_complexity
        ... )
        >>> source = '''
        ...     def maturity(cheese):
        ...         if cheese.years > 5:
        ...             return "seriously mature"
        ...         else:
        ...             return "quite mild"
        ... '''
        >>> results = analyze_methods(
        ...     source, metrics=[
        ...         method_name,
        ...         method_length,
        ...         method_cyclomatic_complexity
        ...     ]
        ... )
        >>> pprint(results)
        [{'method_cyclomatic_complexity': 2,
          'method_length': 3,
          'method_name': 'maturity'}]
        >>> pprint(
        ...     list(
        ...         melt(
        ...             results,
        ...             metrics=[
        ...                 method_length,
        ...                 method_cyclomatic_complexity
        ...             ]
        ...         )
        ...     )
        ... )
        [{'method_name': 'maturity', 'metric_name': 'method_length', 'metric_value': 3},
         {'method_name': 'maturity',
          'metric_name': 'method_cyclomatic_complexity',
          'metric_value': 2}]

    See Also:
        * :py:func:`.assess`

    """
    metric_vars = [m.__name__ for m in metrics]
    first_result, *remaining_results = results
    id_vars = [k for k in first_result.keys() if k not in metric_vars]
    yield from _melt_one(first_result, metric_vars, id_vars)
    for result in remaining_results:
        yield from _melt_one(result, metric_vars, id_vars)


def _melt_one(
    result: NamedMetricResult, metric_vars: typing.List[str], id_vars: typing.List[str]
) -> typing.Iterator[ThresholdBreachDict]:
    id_values = {id_var: result[id_var] for id_var in id_vars}
    for metric_var in metric_vars:
        metric_values = {"metric_name": metric_var, "metric_value": result[metric_var]}
        yield typing.cast(ThresholdBreachDict, id_values | metric_values)
