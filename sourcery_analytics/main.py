"""CLI interface to ``sourcery-analytics``."""
import pathlib
import typing

import typer
import rich

from sourcery_analytics.analysis import assess
from sourcery_analytics.cli.choices import (
    MethodMetricChoice,
    AggregationChoice,
    OutputChoice,
)
from sourcery_analytics.cli.data import ThresholdBreach
from sourcery_analytics.cli.partials import (
    analyze_csv_output,
    analyze_plain_output,
    analyze_rich_output,
    aggregate_csv_output,
    aggregate_plain_output,
    aggregate_rich_output,
    read_settings,
)
from sourcery_analytics.extractors import extract_methods
from sourcery_analytics.logging import set_up_logging
from sourcery_analytics.metrics import method_qualname

app = typer.Typer(rich_markup_mode="rich")


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
    set_up_logging(output)
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

    if output is OutputChoice.RICH:
        analyze_rich_output(method_metric, methods, metrics, sort)
    elif output is OutputChoice.PLAIN:
        analyze_plain_output(methods, metrics, sort)
    elif output is OutputChoice.CSV:
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
    set_up_logging(output)
    # use extract directly here rather than `analyze_methods` in case we want
    # the progressbar
    methods = extract_methods(path)
    metrics = [m.as_method_metric() for m in method_metric]
    aggregation_method = aggregation.as_aggregation()

    if output is OutputChoice.RICH:
        aggregate_rich_output(aggregation, aggregation_method, methods, metrics)

    elif output is OutputChoice.PLAIN:
        aggregate_plain_output(aggregation_method, methods, metrics)

    elif output is OutputChoice.CSV:
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
        "pyproject.toml", file_okay=True, dir_okay=False
    ),
):
    """Using configurable values, will pass or fail according to calculated metrics.

    Exits with code 1 if assessment fails i.e. any methods exceed the thresholds.
    Exits with code 2 for runtime errors, such as mis-configured settings.
    """
    set_up_logging(OutputChoice.RICH)
    console = rich.console.Console()
    metrics = [metric.as_method_metric() for metric in method_metric]

    settings = read_settings(settings_file, console)
    methods = rich.progress.track(extract_methods(path))

    threshold_breach_results = assess(
        methods, metrics=metrics, threshold_settings=settings.thresholds
    )

    count = 0
    for count, threshold_breach_result in enumerate(threshold_breach_results, 1):
        threshold_breach = ThresholdBreach.from_dict(
            threshold_breach_result, threshold_settings=settings.thresholds
        )
        console.print(
            f"{threshold_breach.relative_path}:{threshold_breach.lineno}: "
            f"[bold red]error:[/] "
            f"{threshold_breach.metric_name} of "
            f"[bold]{threshold_breach.method_name}[/] "
            f"is {threshold_breach.metric_value} "
            f"exceeding threshold of {threshold_breach.threshold_value}"
        )

    if count:
        console.print(f"[bold red]Found {count} errors.")
        raise typer.Exit(1)

    console.print("[bold green]Assessment Complete", "[green]No issues found.")


@app.callback()
def callback():
    """Analyze Python source code quality."""


if __name__ == "__main__":
    app()
