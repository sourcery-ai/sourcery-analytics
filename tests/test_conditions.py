import astroid
import pytest

from sourcery_analytics.conditions import is_elif, is_type


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
            elif x < 9:
                print("x-large")
            else:  #@
                print("colossal")  
        """

    def test_ok_if(self, nodes):
        assert not is_elif(nodes[0])

    def test_ok_elif(self, nodes):
        assert is_elif(nodes[1])

    def test_ok_else(self, nodes):
        assert not is_elif(nodes[2])
