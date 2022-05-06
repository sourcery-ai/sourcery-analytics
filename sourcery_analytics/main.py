"""CLI interface to ``sourcery-analytics``."""
import pathlib
import sys
import typing

import typer

from sourcery_analytics import analyze_methods
from sourcery_analytics.cli.choices import (
    MethodMetricChoice,
    AggregationChoice,
    OutputChoice,
)
from sourcery_analytics.cli.partials import (
    analyze_csv_output,
    analyze_plain_output,
    analyze_rich_output,
    aggregate_csv_output,
    aggregate_plain_output,
    aggregate_rich_output,
)
from sourcery_analytics.extractors import extract_methods
from sourcery_analytics.metrics import method_qualname
from sourcery_analytics.settings import Settings

app = typer.Typer()


@app.command(name="analyze")
def cli_analyze(
    path: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    method_metric: typing.List[MethodMetricChoice] = typer.Option(
        [
            "length",
            "cyclomatic_complexity",
            "cognitive_complexity",
            "working_memory",
        ],
    ),
    sort: typing.Optional[MethodMetricChoice] = typer.Option(None),
    output: OutputChoice = typer.Option("rich"),
):
    """Produces a table of method metrics for all methods found in ``path``."""
    if sort is None:
        sort = method_metric[0]
    elif sort not in method_metric:
        raise typer.BadParameter("`--sort` must be one of the method metrics")

    # use extract directly here rather than `analyze_methods` in case we want
    # the progressbar
    methods = extract_methods(path)
    metrics = [
        method_qualname,
        *(metric.as_method_metric() for metric in method_metric),
    ]

    if output is OutputChoice.rich:
        analyze_rich_output(method_metric, methods, metrics, sort)
    elif output is OutputChoice.plain:
        analyze_plain_output(methods, metrics, sort)
    elif output is OutputChoice.csv:
        analyze_csv_output(method_metric, methods, metrics, sort)


@app.command(name="aggregate")
def cli_aggregate(
    path: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    method_metric: typing.List[MethodMetricChoice] = typer.Option(
        [
            "length",
            "cyclomatic_complexity",
            "cognitive_complexity",
            "working_memory",
        ],
    ),
    aggregation: AggregationChoice = typer.Option("average"),
    output: OutputChoice = typer.Option("rich"),
):
    """Produces an aggregate of the metrics for all methods found in ``path``."""
    # use extract directly here rather than `analyze_methods` in case we want
    # the progressbar
    methods = extract_methods(path)
    metrics = [m.as_method_metric() for m in method_metric]
    aggregation_method = aggregation.as_aggregation()

    if output is OutputChoice.rich:
        aggregate_rich_output(aggregation, aggregation_method, methods, metrics)

    elif output is OutputChoice.plain:
        aggregate_plain_output(aggregation_method, methods, metrics)

    elif output is OutputChoice.csv:
        aggregate_csv_output(aggregation_method, method_metric, methods, metrics)


@app.command(name="assess")
def cli_assess(
    path: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    method_metric: typing.List[MethodMetricChoice] = typer.Option(
        [
            "length",
            "cyclomatic_complexity",
            "cognitive_complexity",
            "working_memory",
        ],
    ),
    settings_file: pathlib.Path = typer.Option(
        "pyproject.toml", exists=True, file_okay=True, dir_okay=False
    ),
    output: OutputChoice = typer.Option("rich"),
):
    """Using configurable values, will pass or fail according to calculated metrics."""
    metrics = [
        method_qualname,
        *(metric.as_method_metric() for metric in method_metric),
    ]
    settings = Settings.from_toml_file(settings_file)
    thresholds = {
        f"method_{metric}": threshold_value
        for metric, threshold_value in settings.thresholds.dict().items()
    }
    analysis = analyze_methods(path, metrics=metrics)
    threshold_breaches = []
    for result in analysis:
        for metric_option in method_metric:
            metric_value = result[metric_option.method_method_name]
            threshold_value = thresholds.get(
                metric_option.method_method_name, sys.maxsize
            )
            if metric_value >= threshold_value:
                threshold_breaches.append(
                    (result["method_qualname"], metric_option.value, metric_value)
                )
    if threshold_breaches:
        typer.echo(threshold_breaches)
        raise typer.Exit(1)


@app.callback()
def callback():
    """Analyze Python source code quality."""


if __name__ == "__main__":
    app()
