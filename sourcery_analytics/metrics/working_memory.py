"""Working memory calculations.

The working memory is motivated by considering the number of pieces of information it is necessary to keep
in mind while reading a piece of code. High working memory implies the code may have too many "moving parts"
and could be simplified. The implementation of the calculation is described in the classes below.
"""
import contextlib
import typing

import astroid

from sourcery_analytics.extractors import extract
from sourcery_analytics.utils import nodedispatch
from sourcery_analytics.validators import validate_node_type
from sourcery_analytics.visitors import (
    TreeVisitor,
    Visitor,
)


@nodedispatch
@validate_node_type(astroid.nodes.FunctionDef)
def method_working_memory(method: astroid.nodes.FunctionDef) -> int:
    """Calculates the peak working memory within a method.

    Args:
        method: a node for a function definition

    Examples:
        >>> method_working_memory("def add(a, b): return a + b")
        2
    """
    visitor = TreeVisitor[int, int](WorkingMemoryVisitor(), max)
    return visitor.visit(method)


class WorkingMemoryVisitor(Visitor[int]):
    """Visitor to calculate the working memory of a node.

    Working memory is contextual. Alone, its value is the number of variables,
    including attributes and function calls, within the node. Within conditionals,
    this value is incremented by the number of variables used in the conditional.
    If variables are assigned before the node, these also increment the working memory.
    """

    def __init__(
        self, _condition_penalty: int = 0, _scoped_variables: typing.Set[str] = None
    ):
        if _scoped_variables is None:
            _scoped_variables = set()
        self.condition_penalty: int = _condition_penalty
        self.scoped_variables: typing.Set[str] = _scoped_variables

    @contextlib.contextmanager
    def _enter(self, node: astroid.nodes.NodeNG):
        if isinstance(node, astroid.nodes.If):
            condition_penalty = len(get_names(node.test))
            self.condition_penalty += condition_penalty
            yield
            self.condition_penalty -= condition_penalty
        elif isinstance(node, astroid.nodes.AssignName):
            self.scoped_variables.add(node.name)
            yield
        else:
            yield

    def _touch(self, node: astroid.nodes.NodeNG) -> int:
        unused_variables = self.scoped_variables - get_names(node)
        if isinstance(node, astroid.nodes.If):
            # this is the same as any pre-existing condition penalties less the penalty for this node
            return len(unused_variables) + self.condition_penalty
        if isinstance(node, astroid.nodes.For):
            return (
                len(unused_variables)
                + len(get_names(node.iter))
                + len(get_names(node.target))
                + self.condition_penalty
            )
        if isinstance(node, (astroid.nodes.FunctionDef, astroid.nodes.ClassDef)):
            return 0
        if isinstance(node, astroid.nodes.Statement):
            statement_variables = get_names(node)
            return (
                len(statement_variables)
                + len(unused_variables)
                + self.condition_penalty
            )
        return 0


def get_names(node: astroid.nodes.NodeNG) -> typing.Set[str]:
    """Returns the set of variable names in the node."""
    return set(extract(node, function=get_name))


def get_name(node: astroid.nodes.NodeNG) -> typing.Optional[str]:
    """The name of a single relevant node."""
    if isinstance(node, astroid.nodes.Name):
        return node.name
    if isinstance(node, astroid.nodes.AssignName):
        return node.name
    if isinstance(node, astroid.nodes.Attribute):
        return node.attrname
    return None
