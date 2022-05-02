"""Extract nodes from various sources according to conditions."""
import dataclasses
import functools
import itertools
import pathlib
import typing

import astroid
import astroid.manager

from sourcery_analytics.conditions import Condition, is_method
from sourcery_analytics.visitors import (
    Visitor,
    FunctionVisitor,
    IdentityVisitor,
    TreeVisitor,
    ConditionalVisitor,
)

Extractable = typing.Union[str, astroid.nodes.NodeNG, pathlib.Path]
T = typing.TypeVar("T")
N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)


def extract_methods(item: Extractable, /) -> typing.Iterator[astroid.nodes.FunctionDef]:
    """Extracts methods from the input.

    Args:
        item: source code, node, or path to file or directory

    Returns:
        An iterable of all the function definition nodes in the item

    >>> [method.name for method in extract_methods('''def foo(): pass''')]
    ['foo']

    """
    return extract(item, condition=is_method)


def extract(
    item: Extractable,
    /,
    condition: typing.Optional[Condition] = None,
    function: typing.Optional[
        typing.Callable[[astroid.nodes.NodeNG], typing.Optional[T]]
    ] = None,
) -> typing.Iterator[T]:
    """Extracts from ``item`` according to ``condition`` OR ``function``.

    Args:
        item: source code, node, or path to file or directory
        condition: a condition on a node
        function: a function over a node, returning None for unextracted nodes

    Returns:
        If ``condition`` is specified, an iterable of nodes satisfying the condition.
        If ``function`` is specified, an iterable of not-None results of the function.

    Raises:
        ValueError: if both function and condition are specified

    Examples:
        >>> from sourcery_analytics.conditions import is_name
        >>> [name.name for name in extract('''def add(x, y): x + y''', condition=is_name)]
        ['x', 'y']
        >>> list(extract('''def add(x, y): x + y''', function=lambda node: node.name if hasattr(node, 'name') else None))
        ['add', 'x', 'y', 'x', 'y']

    """
    if condition and function:
        raise ValueError("Please provide only one of ``condition`` or ``function``.")
    elif condition:
        extractor = Extractor[T].from_condition(condition)
    elif function:
        extractor = Extractor.from_function(function)
    else:
        # Fall back to just extracting all the nodes.
        extractor = Extractor[N]()
    return extractor.extract(item)


@dataclasses.dataclass
class Extractor(typing.Generic[T]):
    """Extracts results by walking a tree with the provided visitor.

    The visitor should return either an object of type ``T`` (for instance a node)
    or None. The ``extract`` method will return only the not-None values.

    By default, the extractor will return every node in the tree.

    Examples:
        >>> source = '''
        ...     def one():
        ...         return 1
        ...     def two():
        ...         return 2
        ... '''
        >>> from sourcery_analytics.conditions import is_method, is_const
        >>> methods = Extractor.from_condition(is_method).extract(source)
        >>> list(m.name for m in methods)
        ['one', 'two']
        >>> const_value_extractor = Extractor.from_function(lambda node: node.value if is_const(node) else None)
        >>> const_values = const_value_extractor.extract(source)
        >>> list(const_values)
        [1, 2]
    """

    visitor: Visitor[typing.Optional[T]] = IdentityVisitor()

    @classmethod
    def from_condition(
        cls, condition: Condition, sub_visitor: Visitor[T] = IdentityVisitor()
    ) -> "Extractor[T]":
        """Construct a node extractor from a condition on a node."""
        return cls(ConditionalVisitor(sub_visitor, condition))

    @classmethod
    def from_function(
        cls, function: typing.Callable[[astroid.nodes.NodeNG], typing.Optional[T]]
    ) -> "Extractor[T]":
        """Construct an arbitrary extractor from a function of a node."""
        return cls(FunctionVisitor(function))

    @functools.singledispatchmethod
    def extract(self, item: Extractable) -> typing.Iterator[T]:
        """Extract from source code, a node, a file, or directory."""
        # Note we use regular dispatch rather than nodedispatch for this function
        # in order to support directories as well as files
        raise NotImplementedError(f"Unable to extract from {item}.")

    @extract.register
    def _extract_from_node(self, node: astroid.nodes.NodeNG) -> typing.Iterator[T]:
        visitor = TreeVisitor[typing.Optional[T], typing.Iterator[typing.Optional[T]]](
            self.visitor
        )
        yield from filter(None, visitor.visit(node))

    @extract.register
    def _extract_from_source(self, source: str) -> typing.Iterator[T]:
        node = astroid.parse(source)
        yield from self._extract_from_node(node)

    @extract.register
    def _extract_from_path(self, path: pathlib.Path) -> typing.Iterator[T]:
        if path.is_file():
            return self._extract_from_file(path)
        elif path.is_dir():
            return self._extract_from_directory(path)
        else:  # pragma: no cover
            raise NotImplementedError(
                f"Unable to extract from {path}: not a file or directory."
            )

    def _extract_from_directory(self, directory: pathlib.Path) -> typing.Iterator[T]:
        files = directory.glob("**/*.py")
        yield from itertools.chain.from_iterable(
            self._extract_from_file(file) for file in files
        )

    def _extract_from_file(self, file: pathlib.Path) -> typing.Iterator[T]:
        manager = astroid.manager.AstroidManager()
        module = manager.ast_from_file(file)
        yield from self._extract_from_node(module)
