"""A decorator to check a node's type before performing a (potentially incorrect) calculation."""
import functools
import typing

import astroid

T = typing.TypeVar("T")


class InvalidNodeTypeError(ValueError):
    """Raised when a node's type is validated and found to be incorrect."""


def validate_node_type(*types: typing.Type[astroid.nodes.NodeNG]):
    """Wraps any method taking a node as its first argument and validates the node's type.

    Args:
        *types: any subclasses of :py:class:`astroid.nodes.NodeNG`

    Raises:
        InvalidNodeTypeError: If the passed node doesn't match one of the allowed types.

    Examples:
        >>> @validate_node_type(astroid.nodes.Const)
        ... def is_int(node: astroid.nodes.Const):
        ...     return isinstance(node.value, int)
        >>> expr = astroid.extract_node('5 + 4')
        >>> is_int(expr.left)
        True
        >>> is_int(expr)
        Traceback (most recent call last):
        sourcery_analytics.validators.InvalidNodeTypeError: is_int is not defined for nodes of type <class 'astroid.nodes.node_classes.BinOp'>. Allowed types are: (<class 'astroid.nodes.node_classes.Const'>,).
    """

    def wrap(
        fn: typing.Callable[[astroid.nodes.NodeNG], T]
    ) -> typing.Callable[[astroid.nodes.NodeNG], T]:
        @functools.wraps(fn)
        def wrapped(node: astroid.nodes.NodeNG) -> T:
            if not isinstance(node, types):
                raise InvalidNodeTypeError(
                    f"{fn.__name__} is not defined for nodes of type {type(node)}. Allowed types are: {types}."
                )
            return fn(node)

        return wrapped

    return wrap
