import pytest
from typer.testing import CliRunner

from sourcery_analytics.main import app
from sourcery_analytics.utils import clean_source


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def source():
    return """
        def foo(x, y):
            if x:
                if y:
                    return x + y
            return None
    """


@pytest.fixture
def directory(tmp_path, file):
    path_2 = tmp_path / "file2.py"
    source_2 = clean_source(
        """
            def bar(p):
                for i in p:
                    print(i)
        """
    )
    path_2.write_text(source_2)


@pytest.mark.parametrize(
    "options, exit_code",
    [
        ([], 0),
        (["--method-metric", "length"], 0),
        (["--method-metric", "cognitive_complexity"], 0),
        (["--method-metric", "nonsense"], 2),
        (["--not-an-option", "whatever"], 2),
        (["--method-metric", "length", "--sort", "cognitive_complexity"], 2),
        (
            [
                "--method-metric",
                "length",
                "--method-metric",
                "cognitive_complexity",
                "--sort",
                "cognitive_complexity",
            ],
            0,
        ),
    ],
)
@pytest.mark.parametrize("output", ["rich", "plain", "csv"])
def test_options(cli_runner, file_path, file, options, output, exit_code):
    """Check analysis works for relevant combinations of options."""
    result = cli_runner.invoke(
        app, ["analyze", str(file_path), *options, "--output", output]
    )
    assert result.exit_code == exit_code


def test_analyze_file_plain(cli_runner, file_path, file):
    """Check analysis over file produces correct plain answer."""
    result = cli_runner.invoke(app, ["analyze", str(file_path), "--output", "plain"])
    assert result.exit_code == 0
    assert (
        result.stdout == f"[{{"
        f"'method_qualname': '{file_path}.foo', "
        f"'method_length': 4, "
        f"'method_cyclomatic_complexity': 2, "
        f"'method_cognitive_complexity': 3, "
        f"'method_working_memory': 4"
        f"}}]\n"
    )


def test_analyze_directory_plain(cli_runner, tmp_path, directory):
    """Check analysis over directory produces correct plain answer."""
    result = cli_runner.invoke(app, ["analyze", str(tmp_path), "--output", "plain"])
    assert result.exit_code == 0
    assert (
        result.stdout == f"[{{"
        f"'method_qualname': '{tmp_path}/file.py.foo', "
        f"'method_length': 4, "
        f"'method_cyclomatic_complexity': 2, "
        f"'method_cognitive_complexity': 3, "
        f"'method_working_memory': 4"
        f"}}, "
        f"{{"
        f"'method_qualname': '{tmp_path}/file2.py.bar', "
        f"'method_length': 2, "
        f"'method_cyclomatic_complexity': 1, "
        f"'method_cognitive_complexity': 1, "
        f"'method_working_memory': 3"
        f"}}"
        f"]\n"
    )


def test_analyze_file_csv(cli_runner, file_path, file):
    """Check analysis over directory produces correct CSV answer."""
    result = cli_runner.invoke(app, ["analyze", str(file_path), "--output", "csv"])
    assert result.exit_code == 0
    assert (
        result.stdout
        == f"qualname,length,cyclomatic_complexity,cognitive_complexity,working_memory\n"
        f"{file_path}.foo,4,2,3,4\n"
        f"\n"
    )


@pytest.mark.parametrize(
    "options, exit_code",
    [
        ([], 0),
        (["--method-metric", "length"], 0),
        (["--method-metric", "nonsense"], 2),
        (["--nonsense-option", "whatever"], 2),
        (["--nonsense-option", "whatever"], 2),
        (["--method-metric", "length", "--method-metric", "cognitive_complexity"], 0),
    ],
)
@pytest.mark.parametrize("output", ["rich", "plain", "csv"])
def test_aggregate_options(cli_runner, tmp_path, directory, options, output, exit_code):
    """Check aggregation works for relevant combinations of options."""
    result = cli_runner.invoke(
        app, ["aggregate", str(tmp_path), *options, "--output", output]
    )
    assert result.exit_code == exit_code


@pytest.mark.parametrize(
    "aggregation, expected",
    [
        (
            "average",
            "{'method_length': 3.0, 'method_cyclomatic_complexity': 1.5, 'method_cognitive_complexity': 2.0, 'method_working_memory': 3.5}\n",
        ),
        (
            "total",
            "{'method_length': 6, 'method_cyclomatic_complexity': 3, 'method_cognitive_complexity': 4, 'method_working_memory': 7}\n",
        ),
    ],
)
def test_aggregate_results(cli_runner, tmp_path, directory, aggregation, expected):
    """Check aggregation over results produces correct plain answer."""
    result = cli_runner.invoke(
        app,
        [
            "aggregate",
            str(tmp_path),
            "--output",
            "plain",
            "--aggregation",
            aggregation,
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == expected


@pytest.mark.parametrize(
    "toml_file_source, expected_exit_code",
    [
        (
            """
                [tool.sourcery-analytics.thresholds]
                method_cyclomatic_complexity = 1
            """,
            1,
        ),
        ("", 0),
    ],
)
def test_assess(cli_runner, file, file_path, toml_file, expected_exit_code):
    """Check assess raises correct error pending implementation."""
    result = cli_runner.invoke(
        app, ["assess", str(file_path), "--settings-file", str(toml_file)]
    )
    assert result.exit_code == expected_exit_code


def test_assess_missing_toml(cli_runner, file, file_path):
    result = cli_runner.invoke(
        app, ["assess", str(file_path), "--settings-file", "custom.toml"]
    )
    assert result.exit_code == 0
    assert "Warning" in result.stdout


@pytest.mark.parametrize(
    "toml_file_source",
    [
        """
            [tool.sourcery-analytics.weirdness]
            method_cyclomatic_complexity = 0
        """,
        """
            [tool.sourcery-analytics.thresholds]
            method_cyclomatic_complexity = -1
        """,
    ],
)
def test_assess_bad_toml(cli_runner, file, file_path, toml_file):
    result = cli_runner.invoke(
        app, ["assess", str(file_path), "--settings-file", str(toml_file)]
    )
    assert result.exit_code == 2
    assert "Error" in result.stdout
