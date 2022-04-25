"""Method length calculations.

The length of a method is a simple heuristic for assessing its complexity. In general,
longer methods can be broken up into smaller ones to simplify the code.

Note that for obvious reasons, the method length is only defined for methods.
"""
import astroid.nodes

from sourcery_analytics.validators import validate_node_type
from sourcery_analytics.visitors import TreeVisitor, FunctionVisitor


@validate_node_type(astroid.nodes.FunctionDef)
def method_length(method: astroid.nodes.FunctionDef) -> int:
    """Calculates the method length as the number of statements in the method.

    Args:
        method: a node for a function definition

    Examples:
        >>> method = astroid.extract_node("def add(x, y): z = x + y; return z")
        >>> method_length(method)
        2
    """
    visitor = TreeVisitor(FunctionVisitor(statement_count), collector=sum)
    return visitor.visit(method)


def statement_count(node: astroid.nodes.NodeNG):
    """Count 1 for a statement and 0 otherwise.

    Function and class definitions are skipped.
    """
    if isinstance(
        node,
        (
            astroid.nodes.FunctionDef,
            astroid.nodes.ClassDef,
            astroid.nodes.AsyncFunctionDef,
        ),
    ):
        return 0
    if not isinstance(node, astroid.nodes.Statement):
        return 0
    return 1
