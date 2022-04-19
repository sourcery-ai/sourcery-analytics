"""Method length calculations.

The length of a method is a simple heuristic for assessing its complexity. In general,
longer methods can be broken up into smaller ones to simplify the code.

Note that for obvious reasons, the method length is only defined for methods.
"""
import typing

import astroid

from sourcery_analytics.validators import validate_node_type


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
    return len(method.body)
