"""Utility "metrics" for use in analysis."""
import astroid

from sourcery_analytics.utils import nodedispatch
from sourcery_analytics.validators import validate_node_type


@nodedispatch
@validate_node_type(astroid.nodes.FunctionDef)
def method_qualname(method: astroid.nodes.FunctionDef) -> str:
    """Returns the fully-qualified name of the method.

    If the method was constructed from an object astroid recognizes as a module,
    this will look something like ``"module.method"``, but astroid will
    fall back to the full file path if it can't be sure.

    Examples:
        >>> method = astroid.extract_node("def foo(): pass", module_name="bar")
        >>> method_qualname(method)
        'bar.foo'
    """
    return method.qname()


@nodedispatch
@validate_node_type(astroid.nodes.FunctionDef)
def method_name(method: astroid.nodes.FunctionDef) -> str:
    """Returns the name of the method.

    Not very useful by itself, but can be combined with other metrics for convenience.

    Examples:
        >>> method_name("def foo(): pass")
        'foo'
    """
    return method.name


@nodedispatch
def node_type_name(node: astroid.nodes.NodeNG) -> str:
    """Returns a string representing the type of the node.

    Useful for breakdowns of an AST by node type.

    Examples:
        >>> source = '''
        ...     def x(y, z):  #@
        ...         x = y + z  #@
        ... '''
        >>> nodes = astroid.extract_node(source)
        >>> node_type_name(nodes[0])
        'FunctionDef'
        >>> node_type_name(nodes[1])
        'Assign'
    """
    return node.__class__.__name__
