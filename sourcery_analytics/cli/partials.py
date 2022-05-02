"""Parts of larger commands."""
import operator
import typing

import typer

from sourcery_analytics import analyze
from sourcery_analytics.metrics.compounders import NamedMetricResult


def analyze_rich_output(method_metric, methods, metrics, sort):
    """Perform analysis and display results in a rich-formatted table."""
    import rich.table
    import rich.progress

    console = rich.console.Console()
    methods_progress = rich.progress.track(methods, description="Analyzing methods...")
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


def analyze_plain_output(methods, metrics, sort):
    """Perform analysis and display the python object's representation."""
    analysis = sorted(
        analyze(methods, metrics=metrics),
        key=operator.itemgetter(sort.method_method_name),
        reverse=True,
    )
    typer.echo(analysis)


def analyze_csv_output(method_metric, methods, metrics, sort):
    """Perform analysis and display the results in CSV format."""
    analysis = sorted(
        analyze(methods, metrics=metrics),
        key=operator.itemgetter(sort.method_method_name),
        reverse=True,
    )
    result = ""
    result += (
        "qualname,"
        + ",".join([str(metric_choice.value) for metric_choice in method_metric])
        + "\n"
    )
    for metric in analysis:
        result += ",".join([str(value) for _sub_metric_name, value in metric]) + "\n"
    typer.echo(result)


def aggregate_rich_output(aggregation, aggregation_method, methods, metrics):
    """Perform an aggregated analysis and display the results in a rich-formatted table."""
    import rich.table
    import rich.progress

    console = rich.console.Console()
    methods_progress = rich.progress.track(methods, description="Analyzing methods...")
    result = analyze(methods_progress, metrics=metrics, aggregation=aggregation_method)
    table = rich.table.Table()
    table.add_column("Metric")
    table.add_column(f"{aggregation.value.title()} Value", justify="right")
    for metric_name, metric_value in result:
        table.add_row(metric_name, str(metric_value))
    console.print(table)


def aggregate_plain_output(aggregation_method, methods, metrics):
    """Perform an aggregated analysis and display the python objects' representation."""
    result = analyze(methods, metrics=metrics, aggregation=aggregation_method)
    typer.echo(result)


def aggregate_csv_output(aggregation_method, method_metric, methods, metrics):
    """Perform an aggregated analysis and display the results in CSV format."""
    analysis = analyze(methods, metrics=metrics, aggregation=aggregation_method)
    result = ",".join([m.value for m in method_metric]) + "\n"
    result += ",".join(str(value) for _metric_name, value in analysis)
    typer.echo(result)
