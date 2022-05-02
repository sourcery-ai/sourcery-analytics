import astroid.nodes
import pytest

from sourcery_analytics.utils import nodedispatch, clean_source


class TestCleanSource:
    def test_clean_source(self):
        source = """
            if thing:
                whatever()
        """
        result = clean_source(source)
        assert result == "if thing:\n    whatever()"


class TestNodeDispatch:
    @pytest.fixture
    def source(self):
        return """
            def add(x, y):
                return x + y
        """

    @pytest.fixture
    def node_checker(self):
        def node_function(node):
            assert isinstance(node, astroid.nodes.NodeNG)

        return node_function

    def test_nodedispatch_source(self, cleaned_source, node_checker):
        dispatch_node_check = nodedispatch(node_checker)
        dispatch_node_check(cleaned_source)

    def test_nodedispatch_node(self, node, node_checker):
        dispatch_node_check = nodedispatch(node_checker)
        dispatch_node_check(node)

    def test_nodedispatch_path(self, file, file_path, node_checker):
        dispatch_node_check = nodedispatch(node_checker)
        dispatch_node_check(file_path)

    def test_nodedispatch_nonsense(self, node_checker):
        dispatch_node_check = nodedispatch(node_checker)
        with pytest.raises(NotImplementedError):
            dispatch_node_check(42)
