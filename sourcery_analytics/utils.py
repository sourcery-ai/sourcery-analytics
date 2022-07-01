"""Functions that don't fit anywhere else."""
import functools
import pathlib
import textwrap
import typing

import astroid
import astroid.manager
import astroid.nodes


N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T")
NT = typing.Union[str, astroid.nodes.NodeNG, pathlib.Path]


def clean_source(source_str: str) -> str:
    r"""Removes whitespace surrounding a source code string.

    Examples:
        >>> source = '''
        ...
        ...     def example():
        ...         return "have a nice day"
        ... '''
        >>> clean_source(source)
        'def example():\n    return "have a nice day"'
    """
    return textwrap.dedent(source_str).strip()


def nodedispatch(node_function: typing.Callable[[N], T]) -> typing.Callable[[NT], T]:
    """Extends compatibility of functions over nodes.

    Converts a function from working only on nodes to working on strings, nodes, and
    file paths.

    Examples:
        >>> @nodedispatch
        ... def node_type(node):
        ...     return node.__class__
        >>> node_type("x")
        <class 'astroid.nodes.node_classes.Name'>
    """
    manager = astroid.manager.AstroidManager()

    @functools.wraps(node_function)
    def wrapped(item: NT) -> T:
        if isinstance(item, astroid.nodes.NodeNG):
            return node_function(item)
        if isinstance(item, str):
            node = astroid.extract_node(item)
            return node_function(node)
        if isinstance(item, pathlib.Path):
            node = manager.ast_from_file(item)
            return node_function(node)
        raise NotImplementedError(
            f"Unable to coerce item of type {type(item)} into a node."
        )

    return wrapped


class InvalidNodeTypeError(ValueError):
    """Raised when a node's type is validated and found to be incorrect."""


def validate_node_type(*types: typing.Type[astroid.nodes.NodeNG]):
    """Wraps any node function and validates the node's type.

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
        sourcery_analytics.utils.InvalidNodeTypeError...
    """

    def wrap(
        node_function: typing.Callable[[astroid.nodes.NodeNG], T]
    ) -> typing.Callable[[astroid.nodes.NodeNG], T]:
        @functools.wraps(node_function)
        def wrapped(node: astroid.nodes.NodeNG) -> T:
            if not isinstance(node, types):
                raise InvalidNodeTypeError(
                    f"{node_function.__name__} is not defined "
                    f"for nodes of type {type(node)}. "
                    f"Allowed types are: {types}."
                )
            return node_function(node)

        return wrapped

    return wrap
