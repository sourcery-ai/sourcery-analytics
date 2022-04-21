import itertools
import operator
import pathlib
import typing

import astroid.manager
import typer

from sourcery_analytics.analysis import Analyzer
from sourcery_analytics.cli import (
    MethodMetricChoice,
    AggregationChoice,
    CollectorChoice,
    OutputChoice,
)
from sourcery_analytics.conditions import is_type
from sourcery_analytics.extractors import Extractor

T = typing.TypeVar("T")

app = typer.Typer()


@app.command()
def analyze(
    path: pathlib.Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=True,
    ),
    method_metric: typing.List[MethodMetricChoice] = typer.Option(
        [
            "qualname",
            "length",
            "cyclomatic_complexity",
            "cognitive_complexity",
            "working_memory",
        ],
    ),
    sort: typing.Optional[MethodMetricChoice] = typer.Option(None),
    output: OutputChoice = typer.Option("rich"),
):
    if sort is None:
        sort = method_metric[0]
    elif sort not in method_metric:
        raise typer.BadParameter("`--sort` must be one of the method metrics")
    analyzer = Analyzer.from_choices(
        *method_metric,
        collector_choice=CollectorChoice.name,
        aggregation_choice=AggregationChoice.collect,
    )
    manager = astroid.manager.AstroidManager()
    method_extractor = Extractor.from_condition(is_type(astroid.nodes.FunctionDef))

    if path.is_file():
        module = manager.ast_from_file(path)
        methods = method_extractor.extract(module)
    elif path.is_dir():
        files = path.glob("**/*.py")
        modules = (manager.ast_from_file(file) for file in files)
        methods = itertools.chain.from_iterable(
            method_extractor.extract(module) for module in modules
        )
    else:
        raise NotImplementedError(f"Unable to analyze path {path}.")

    if output is OutputChoice.rich:
        import rich.console
        import rich.table

        console = rich.console.Console()
        with console.status("Analyzing..."):
            result = analyzer.analyze(methods)
        console.print("[bold green]Analysis Complete")
        table = rich.table.Table()
        for metric in method_metric:
            table.add_column(metric.value, justify="right")
        for metric in sorted(
            result,
            key=operator.itemgetter(sort.method_method_name),
            reverse=True,
        ):
            table.add_row(
                *(
                    f"{value:.2f}" if isinstance(value, (float, int)) else str(value)
                    for _sub_metric_name, value in metric
                )
            )
        console.print(table)
    else:
        result = analyzer.analyze(methods)
        typer.echo(
            sorted(
                result,
                key=operator.itemgetter(sort.method_method_name),
                reverse=True,
            )
        )


@app.command()
def aggregate():
    # if (
    #         collector is CollectorChoice.name
    #         and aggregation is not AggregationChoice.collect
    # ):
    #     table = rich.table.Table()
    #     table.add_column("Metric")
    #     table.add_column(f"{aggregation.value.title()} Value", justify="right")
    #     for metric, value in result.items():
    #         table.add_row(
    #             metric,
    #             f"{value:.2f}" if isinstance(value, (float, int)) else str(value),
    #         )
    #     console.print(table)
    raise NotImplementedError("Coming soon.")


@app.callback()
def callback():
    """
    Analyze Python source code quality.
    """


if __name__ == "__main__":
    app()
