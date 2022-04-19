"""Utility "metric" for the method name."""
import astroid

from sourcery_analytics.validators import validate_node_type


@validate_node_type(astroid.nodes.FunctionDef)
def method_itself(method: astroid.nodes.FunctionDef) -> astroid.nodes.FunctionDef:
    return method


@validate_node_type(astroid.nodes.FunctionDef)
def method_qualname(method: astroid.nodes.FunctionDef) -> str:
    return method.qname()


@validate_node_type(astroid.nodes.FunctionDef)
def method_name(method: astroid.nodes.FunctionDef) -> str:
    """Returns the name of the method.

    Not very useful by itself, but can be combined with other metrics for convenience.

    Examples:
        >>> method = astroid.extract_node("def foo(): pass")
        >>> method_name(method)
        'foo'
    """
    return method.name
