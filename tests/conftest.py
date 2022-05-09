import typing

import astroid
import pytest

from sourcery_analytics.utils import clean_source


@pytest.fixture
def source() -> str:
    ...


@pytest.fixture
def cleaned_source(source) -> str:
    return clean_source(source)


@pytest.fixture
def nodes(cleaned_source) -> typing.List[astroid.nodes.NodeNG]:
    return astroid.extract_node(cleaned_source)


@pytest.fixture
def node(cleaned_source) -> astroid.nodes.NodeNG:
    return astroid.extract_node(cleaned_source)


@pytest.fixture
def module(cleaned_source) -> astroid.nodes.Module:
    return astroid.parse(cleaned_source)


@pytest.fixture
def file_path(tmp_path):
    return tmp_path / "file.py"


@pytest.fixture
def file(file_path, cleaned_source):
    file_path.write_text(cleaned_source)


@pytest.fixture
def toml_file_path(tmp_path):
    return tmp_path / "pyproject.toml"


@pytest.fixture
def toml_file_source():
    return """
        [tool.sourcery-analytics.thresholds]
        method_cyclomatic_complexity = 5
    """


@pytest.fixture
def toml_file(toml_file_path, toml_file_source):
    toml_file_path.write_text(clean_source(toml_file_source))
    return toml_file_path
