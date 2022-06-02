import astroid.nodes
import pytest

from sourcery_analytics import extract_methods, extract
from sourcery_analytics.conditions import is_const
from sourcery_analytics.extractors import Extractor


@pytest.fixture
def source():
    return """
        def one():
            return 1
        def two():
            return "two"
    """


class TestExtractMethods:
    def test_extract_methods_source(self, cleaned_source):
        result = list(extract_methods(cleaned_source))
        assert all(isinstance(n, astroid.nodes.FunctionDef) for n in result)
        assert [n.name for n in result] == ["one", "two"]

    def test_extract_methods_node(self, module):
        result = list(extract_methods(module))
        assert all(isinstance(n, astroid.nodes.FunctionDef) for n in result)
        assert [n.name for n in result] == ["one", "two"]

    def test_extract_methods_path(self, file_path, file):
        result = list(extract_methods(file_path))
        assert all(isinstance(n, astroid.nodes.FunctionDef) for n in result)
        assert [n.name for n in result] == ["one", "two"]


class TestExtract:
    def test_extract(self, cleaned_source):
        result = list(extract(cleaned_source))
        assert len(result) == 9

    def test_extract_source_function(self, cleaned_source):
        result = list(extract(cleaned_source, function=is_const))
        assert result == [True, True]

    def test_extract_source_condition(self, cleaned_source):
        nodes = list(extract(cleaned_source, condition=is_const))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_clash(self, cleaned_source):
        with pytest.raises(ValueError):
            extract(cleaned_source, condition=is_const, function=is_const)


class TestExtractor:
    @pytest.fixture
    def extractor(self):
        return Extractor.from_condition(is_const)

    def test_from_condition(self, cleaned_source):
        extractor = Extractor.from_condition(is_const)
        nodes = list(extractor.extract(cleaned_source))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_from_function(self, cleaned_source):
        extractor = Extractor.from_function(is_const)
        result = list(extractor.extract(cleaned_source))
        assert result == [True, True]

    def test_extract_from_node(self, extractor, module):
        nodes = list(extractor.extract(module))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_extract_from_source(self, extractor, cleaned_source):
        nodes = list(extractor.extract(cleaned_source))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_extract_from_file(self, extractor, file_path, file):
        nodes = list(extractor.extract(file_path))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_extract_from_directory(self, extractor, tmp_path, file):
        nodes = list(extractor.extract(tmp_path))
        result = [node.value for node in nodes]
        assert result == [1, "two"]

    def test_extract_from_nonsense(self, extractor):
        with pytest.raises(NotImplementedError):
            extractor.extract(8)

    @pytest.mark.parametrize(
        "source",
        [
            """
                def foo():
            """,
        ],
    )
    def test_extract_with_syntax_error(self, extractor, file_path, file):
        with pytest.warns(SyntaxWarning):
            nodes = list(extractor.extract(file_path))
            assert not nodes
