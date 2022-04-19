import pytest

from sourcery_analytics.metrics import method_cyclomatic_complexity
from sourcery_analytics.metrics.cyclomatic_complexity import cyclomatic_complexity


class TestMethodCyclomaticComplexity:
    @pytest.fixture
    def source(self):
        return """
            def zero(): #@
                return 1
                
            def one(x): #@
                if x > 2:
                    return 2
                return x
            
            def two(x, y): #@
                if x and y:
                    return x
                return y
        """

    def test_ok_zero(self, nodes):
        result = method_cyclomatic_complexity(nodes[0])
        assert result == 0

    def test_ok_one(self, nodes):
        result = method_cyclomatic_complexity(nodes[1])
        assert result == 1

    def test_ok_two(self, nodes):
        result = method_cyclomatic_complexity(nodes[2])
        assert result == 2


@pytest.mark.parametrize(
    "source",
    [
        """
            def elif_chain(x):
                if x < 3:
                    print("small")
                elif x < 5:
                    print("medium")
                elif x < 7:
                    print("large")
                elif x < 9:
                    print("x-large")
                else:
                    print("colossal")          
        """
    ],
)
def test_ok_elif_chains(node):
    result = method_cyclomatic_complexity(node)
    assert result == 5


class TestCyclomaticComplexity:
    @pytest.mark.parametrize(
        "source",
        [
            """
                try:
                    whatever()
                except ValueError:
                    print("nope")
            """
        ],
    )
    def test_ok_except_1(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                try:
                    whatever()
                except ValueError:
                    print("nope")
                except Exception as e:
                    raise SeriousError from e
            """
        ],
    )
    def test_ok_except_2(self, node):
        result = cyclomatic_complexity(node)
        assert result == 2

    @pytest.mark.parametrize("source", ["a and b"])
    def test_ok_boolop_1(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize("source", ["a and b and c"])
    def test_ok_boolop_2(self, node):
        result = cyclomatic_complexity(node)
        assert result == 2

    @pytest.mark.parametrize("source", ["a and b or c"])
    def test_ok_boolop_mixed(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize("source", ["if x: 'y'"])
    def test_ok_if(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                if x: 
                    'y'
                else:
                    'z'
            """
        ],
    )
    def test_ok_if_else(self, node):
        result = cyclomatic_complexity(node)
        assert result == 2

    @pytest.mark.parametrize(
        "source",
        [
            """
                if x: 
                    'y'
                elif xx:
                    'yy'
                else:
                    'z'
            """
        ],
    )
    def test_ok_if_elif_else(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                for x in xs:
                    print(x)
            """
        ],
    )
    def test_ok_for_1(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                for x in xs:
                    print(x)
                else:
                    print(xs)
            """
        ],
    )
    def test_ok_for_2(self, node):
        result = cyclomatic_complexity(node)
        assert result == 2

    @pytest.mark.parametrize(
        "source",
        [
            """
                while x in xs:
                    print(x)
            """
        ],
    )
    def test_ok_while_1(self, node):
        result = cyclomatic_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                while x in xs:
                    print(x)
                else:
                    print(xs)
            """
        ],
    )
    def test_ok_while_2(self, node):
        result = cyclomatic_complexity(node)
        assert result == 2

    @pytest.mark.parametrize("source", ["[x for x in xs if x > 3]"])
    def test_ok_comprehension(self, node):
        result = cyclomatic_complexity(node.generators[0])
        assert result == 2

    @pytest.mark.parametrize(
        "source",
        [
            "5 + 3",
            "a",
            "a + b",
            "print(x)",
            "def foo(): pass",
        ],
    )
    def test_ok_zero(self, node):
        assert cyclomatic_complexity(node) == 0
