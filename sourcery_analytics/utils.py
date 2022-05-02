"""Functions that don't fit anywhere else."""
import functools
import pathlib
import textwrap
import typing

import astroid.manager
import astroid.nodes

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


def nodedispatch(fn):
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
    def wrapped(item: NT, *args, **kwargs) -> T:
        if isinstance(item, astroid.nodes.NodeNG):
            return fn(item, *args, **kwargs)
        if isinstance(item, str):
            node = astroid.extract_node(item)
            return fn(node, *args, **kwargs)
        if isinstance(item, pathlib.Path):
            node = manager.ast_from_file(item)
            return fn(node, *args, **kwargs)
        raise NotImplementedError(
            f"Unable to coerce item of type {type(item)} into a node."
        )

    return wrapped
