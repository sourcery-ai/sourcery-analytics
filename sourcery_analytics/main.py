"""CLI interface to ``sourcery-analytics``."""
import pathlib
import typing

import typer

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
def cli_assess():
    """Using configurable values, will pass or fail according to calculated metrics."""
    raise NotImplementedError("Coming soon!")


@app.callback()
def callback():
    """Analyze Python source code quality."""


if __name__ == "__main__":
    app()
