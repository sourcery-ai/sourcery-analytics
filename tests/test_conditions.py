import astroid
import pytest

from sourcery_analytics.conditions import (
    is_elif,
    is_type,
    always,
    is_method,
    is_const,
    is_name,
)


class TestAlways:
    @pytest.mark.parametrize("source", ["x + y", "foo()", "pass"])
    def test_ok(self, node):
        assert always(node)


class TestIsType:
    @pytest.mark.parametrize(
        "source, types",
        [
            ("x + y", (astroid.nodes.BinOp,)),
            ("x + y", (astroid.nodes.BinOp, astroid.nodes.Expr)),
            ("pass", (astroid.nodes.Pass, astroid.nodes.Statement)),
        ],
    )
    def test_ok(self, node, types):
        assert is_type(*types)(node)

    @pytest.mark.parametrize(
        "source, types",
        [
            ("x + y", (astroid.nodes.Statement,)),
            ("x + y", (astroid.nodes.BoolOp,)),
            ("pass", (astroid.nodes.Name,)),
        ],
    )
    def test_neg(self, node, types):
        assert not is_type(*types)(node)


class TestIsElif:
    @pytest.fixture
    def source(self):
        return """
            if x < 3:  #@
                print("small")
            elif x < 5:  #@
                print("medium")
            elif x < 7:
                print("large")
            elif x < 9:  #@
                print("x-large")
            else:
                print("colossal")  #@
        """

    def test_ok_if(self, nodes):
        assert not is_elif(nodes[0])

    def test_ok_elif(self, nodes):
        assert is_elif(nodes[1])
        assert is_elif(nodes[2])

    def test_ok_else(self, nodes):
        assert not is_elif(nodes[3].parent)


class TestIsMethod:
    @pytest.fixture
    def source(self):
        return """
            def add(x, y):  #@
                return x + y  #@
        """

    def test_ok(self, nodes):
        assert is_method(nodes[0])

    def test_neg(self, nodes):
        assert not is_method(nodes[1])


class TestIsConst:
    @pytest.fixture
    def source(self):
        return """
            def minus_one(x):
                return __(x) - __(1)
        """

    def test_ok(self, nodes):
        assert is_const(nodes[1])

    def test_neg(self, nodes):
        assert not is_const(nodes[0])


class TestIsName:
    @pytest.fixture
    def source(self):
        return """
            def minus_one(x):
                return __(x) - __(1)
        """

    def test_ok(self, nodes):
        assert is_name(nodes[0])

    def test_neg(self, nodes):
        assert not is_name(nodes[1])
