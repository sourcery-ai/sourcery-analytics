"""Cognitive complexity calculations.

Cognitive complexity is intended to reflect the difficulty in understanding deeply-nested
code, especially nested conditionals.
"""
import astroid
import contextlib

from sourcery_analytics.conditions import is_elif
from sourcery_analytics.validators import validate_node_type
from sourcery_analytics.visitors import Visitor, TreeVisitor


@validate_node_type(astroid.nodes.FunctionDef)
def method_cognitive_complexity(method: astroid.nodes.FunctionDef) -> int:
    """Calculates the total cognitive complexity of the method as the total complexity of its body.

    Args:
        method: a node for a function definition

    Examples:
        >>> source = '''
        ...     def check_add(x, y):
        ...         if x:
        ...             if y:
        ...                 return x + y
        ... '''
        >>> method = astroid.parse(source).body[0]
        >>> method_cognitive_complexity(method)
        3
    """
    visitor = TreeVisitor[int, int](CognitiveComplexityVisitor(), sum)
    return visitor.visit(method)


class CognitiveComplexityVisitor(Visitor[int]):
    """Visitor to calculate the cognitive complexity of a node.

    Cognitive complexity is contextual. Alone, its value is 1 for control flow elements.
    It is incremented by 1 for each level of "nesting" within control flow structures.
    """

    def __init__(self, _nesting=0):
        self.nesting = _nesting

    @contextlib.contextmanager
    def _enter(self, node: astroid.nodes.NodeNG):
        if is_elif(node):
            yield  # the nesting has already been incremented
        elif isinstance(
            node,
            (
                astroid.nodes.If,
                astroid.nodes.IfExp,
                astroid.nodes.For,
                astroid.nodes.While,
                astroid.nodes.ExceptHandler,
            ),
        ):
            self.nesting += 1
            yield
            self.nesting -= 1
        else:
            yield

    def visit(self, node: astroid.nodes.NodeNG) -> int:
        """Returns the cognitive complexity of a single node.

        If statements, if expressions, for statements, while expressions, and
        except blocks all have a cognitive complexity of 1.
        """
        if (
            isinstance(node, astroid.nodes.If)
            and node.orelse
            and not is_elif(node.orelse[0])
        ) or isinstance(node, astroid.nodes.IfExp):
            return self.nesting + 1  # count one extra for else statements
        elif isinstance(
            node,
            (
                astroid.nodes.If,
                astroid.nodes.For,
                astroid.nodes.While,
                astroid.nodes.ExceptHandler,
            ),
        ):
            return self.nesting
        return 0
