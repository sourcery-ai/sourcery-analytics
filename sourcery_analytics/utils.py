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
    r"""Remove whitespace surrounding a source code string.

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


def nodedispatch(fn: typing.Callable[[N], T]) -> typing.Callable[[NT], T]:
    """Convert a function from one that works only on nodes to one that works on strings, nodes, and file paths.

    Examples:
        >>> @nodedispatch
        ... def node_type(node):
        ...     return node.__class__
        >>> node_type("x")
        <class 'astroid.nodes.node_classes.Name'>
    """
    manager = astroid.manager.AstroidManager()

    @functools.wraps(fn)
    def wrapped(item: NT) -> T:
        if isinstance(item, astroid.nodes.NodeNG):
            return fn(item)
        if isinstance(item, str):
            node = astroid.extract_node(item)
            return fn(node)
        if isinstance(item, pathlib.Path):
            node = manager.ast_from_file(item)
            return fn(node)
        raise NotImplementedError(
            f"Unable to coerce item of type {type(item)} into a node."
        )

    return wrapped


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
        sourcery_analytics.utils.InvalidNodeTypeError: is_int is not defined for nodes of type <class 'astroid.nodes.node_classes.BinOp'>. Allowed types are: (<class 'astroid.nodes.node_classes.Const'>,).
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
