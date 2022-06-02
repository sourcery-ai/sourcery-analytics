"""Cyclomatic complexity calculations.

Cyclomatic complexity is a measure of the number of "pathways" through a piece of code, developed
as an aid to writing tests. A high cyclomatic complexity can indicate a piece of code may have
too much branching logic.

For implementation details see methods below.
"""
import astroid

from sourcery_analytics.conditions import is_elif
from sourcery_analytics.utils import nodedispatch, validate_node_type
from sourcery_analytics.visitors import TreeVisitor, FunctionVisitor


@nodedispatch
@validate_node_type(astroid.nodes.FunctionDef)
def method_cyclomatic_complexity(method: astroid.nodes.FunctionDef) -> int:
    """The total cyclomatic complexity of a method.

    Args:
        method: a node for a function definition

    Examples:
        >>> method_cyclomatic_complexity("def div(x, y): return None if y == 0 else x / y")
        2
    """
    return total_cyclomatic_complexity(method)


@nodedispatch
def total_cyclomatic_complexity(node: astroid.nodes.NodeNG) -> int:
    """Computes the total cyclomatic complexity within a node.

    Args:
        node: any node in an astroid syntax tree

    Examples:
         >>> total_cyclomatic_complexity('''if x: pass''')
         1
    """
    visitor = TreeVisitor[int, int](FunctionVisitor(cyclomatic_complexity), sum)
    return visitor.visit(node)


def cyclomatic_complexity(node: astroid.nodes.NodeNG) -> int:
    """The cyclomatic complexity for a single node.

    Cyclomatic complexity is context-free and so doesn't need a visitor to evaluate.

    * Try/Except statements return the number of except (and else) blocks.
    * Boolean operations return one less than the number of compared values.
    * If statements and expressions return 1, plus 1 for each "else" or "elif".
    * For and while statements return 1, plus 1 for any "else".
    * Comprehensions return 1 plus the number of conditions.
    """
    if isinstance(node, astroid.nodes.TryExcept):
        return len(node.handlers) + bool(node.orelse)
    elif isinstance(node, astroid.nodes.BoolOp):
        return len(node.values) - 1
    elif isinstance(node, astroid.nodes.If):
        return 1 + (bool(node.orelse) and not is_elif(node.orelse[0]))
    elif isinstance(node, astroid.nodes.IfExp):
        return 2  # always has two routes
    elif isinstance(node, (astroid.nodes.For, astroid.nodes.While)):
        return bool(node.orelse) + 1
    elif isinstance(node, astroid.nodes.Comprehension):
        return len(node.ifs) + 1
    return 0
