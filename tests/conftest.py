import typing

import astroid
import pytest

from sourcery_analytics.utils import clean_source


@pytest.fixture
def source() -> str:
    ...


@pytest.fixture
def make_node():
    def _make_node(source: str):
        return astroid.extract_node(clean_source(source))

    return _make_node


@pytest.fixture
def nodes(source, make_node) -> typing.List[astroid.nodes.NodeNG]:
    return make_node(source)


@pytest.fixture
def node(source, make_node) -> astroid.nodes.NodeNG:
    return make_node(source)
