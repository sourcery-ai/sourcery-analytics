import astroid
import pytest

from sourcery_analytics.conditions import always, is_type
from sourcery_analytics.visitors import (
    IdentityVisitor,
    FunctionVisitor,
    ConditionalVisitor,
)


class TestIdentityVisitor:
    @pytest.fixture
    def visitor(self):
        return IdentityVisitor()

    @pytest.mark.parametrize(
        "source, expected_name",
        [
            ("x + y", "BinOp"),
            ("y", "Name"),
            ("a = 5", "Assign"),
        ],
    )
    def test_identity_visitor(self, visitor, node, expected_name):
        assert visitor._touch(node).__class__.__name__ == expected_name


class TestFunctionVisitor:
    @pytest.fixture
    def function(self):
        return lambda x: x

    @pytest.fixture
    def visitor(self, function):
        return FunctionVisitor(function)

    @pytest.mark.parametrize(
        "function, source, expected",
        [
            (lambda node: node.__class__.__name__, "x + y", "BinOp"),
            (lambda node: node.__class__.__name__, "y", "Name"),
            (
                lambda node: len(node.body),
                """
                    if x:
                        y = x ** 2
                        return x + y
                """,
                2,
            ),
        ],
    )
    def test_function_visitor(self, visitor, node, expected):
        assert visitor._touch(node) == expected


class TestConditionalVisitor:
    @pytest.fixture
    def sub_visitor(self):
        return IdentityVisitor()

    @pytest.fixture
    def condition(self):
        return always

    @pytest.fixture
    def visitor(self, sub_visitor, condition):
        return ConditionalVisitor(sub_visitor, condition)

    @pytest.mark.parametrize(
        "sub_visitor, condition, source, expected",
        [
            (
                FunctionVisitor(lambda node: len(node.values)),
                is_type(astroid.nodes.BoolOp),
                "a and b",
                2,
            ),
            (
                FunctionVisitor(lambda node: len(node.values)),
                is_type(astroid.nodes.BoolOp),
                "a and b and c and d",
                4,
            ),
            (
                FunctionVisitor(lambda node: len(node.values)),
                is_type(astroid.nodes.BoolOp),
                "2 + 5",
                None,
            ),
            (
                FunctionVisitor(lambda node: len(node.values)),
                is_type(astroid.nodes.BoolOp),
                "all(a, b, c, d)",
                None,
            ),
        ],
    )
    def test_conditional_visitor(self, visitor, node, expected):
        assert visitor._touch(node) == expected
