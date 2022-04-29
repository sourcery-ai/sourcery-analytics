"""CLI interface to ``sourcery-analytics``."""
import operator
import pathlib
import typing

import typer

from sourcery_analytics.analysis import analyze
from sourcery_analytics.cli import (
    MethodMetricChoice,
    OutputChoice,
    AggregationChoice,
)
from sourcery_analytics.extractors import extract_methods
from sourcery_analytics.metrics import method_qualname
from sourcery_analytics.metrics.compounders import NamedMetricResult

T = typing.TypeVar("T")

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
        import rich.console
        import rich.table
        import rich.progress

        console = rich.console.Console()

        methods_progress = rich.progress.track(
            methods, description="Analyzing methods..."
        )
        analysis: typing.List[NamedMetricResult] = sorted(
            analyze(methods_progress, metrics=metrics),
            key=operator.itemgetter(sort.method_method_name),
            reverse=True,
        )

        console.print("[bold green]Analysis Complete")

        table = rich.table.Table()
        table.add_column("Method")
        for metric_choice in method_metric:
            table.add_column(metric_choice.value, justify="right")
        for metric in analysis:
            table.add_row(
                *(
                    f"{value}" if isinstance(value, (float, int)) else str(value)
                    for _sub_metric_name, value in metric
                )
            )

        console.print(table)
        raise typer.Exit()

    analysis = sorted(
        analyze(methods, metrics=metrics),
        key=operator.itemgetter(sort.method_method_name),
        reverse=True,
    )

    if output is OutputChoice.plain:
        typer.echo(analysis)

    elif output is OutputChoice.csv:
        result = ""
        result += (
            "qualname,"
            + ",".join([str(metric_choice.value) for metric_choice in method_metric])
            + "\n"
        )
        for metric in analysis:
            result += (
                ",".join([str(value) for _sub_metric_name, value in metric]) + "\n"
            )
        typer.echo(result)


@app.command(name="aggregate")
def cli_aggregate(
    path: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    metric: typing.List[MethodMetricChoice] = typer.Option(
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
    metrics = [m.as_method_metric() for m in metric]
    aggregation_method = aggregation.as_aggregation()

    if output is OutputChoice.rich:
        import rich.console
        import rich.table
        import rich.progress

        console = rich.console.Console()

        methods_progress = rich.progress.track(
            methods, description="Analyzing methods..."
        )
        result = analyze(
            methods_progress, metrics=metrics, aggregation=aggregation_method
        )

        table = rich.table.Table()
        table.add_column("Metric")
        table.add_column(f"{aggregation.value.title()} Value", justify="right")
        for metric_name, metric_value in result:
            table.add_row(metric_name, str(metric_value))

        console.print(table)

    elif output is OutputChoice.plain:
        result = analyze(methods, metrics=metrics, aggregation=aggregation_method)
        typer.echo(result)

    elif output is OutputChoice.csv:
        raise NotImplementedError


@app.command(name="assess")
def cli_assess():
    """Using configurable values, will pass or fail according to calculated metrics."""
    raise NotImplementedError("Coming soon!")


@app.callback()
def callback():
    """Analyze Python source code quality."""


if __name__ == "__main__":
    app()
