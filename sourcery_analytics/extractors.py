"""Extract nodes from various sources according to conditions."""
import dataclasses
import typing

import astroid

from sourcery_analytics.conditions import Condition
from sourcery_analytics.visitors import (
    Visitor,
    FunctionVisitor,
    IdentityVisitor,
    TreeVisitor,
    ConditionalVisitor,
)

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
T = typing.TypeVar("T")


@dataclasses.dataclass
class Extractor(typing.Generic[T]):
    """Extract results by walking a tree with the provided visitor.

    The visitor should return either an object of type ``T`` (for instance a node)
    or None. The ``extract`` method will return only the not-None values.

    Examples:
        >>> source = '''
        ...     def one():
        ...         return 1
        ...     def two():
        ...         return 2
        ... '''
        >>> from sourcery_analytics.conditions import is_type
        >>> is_method = is_type(astroid.nodes.FunctionDef)
        >>> is_const = is_type(astroid.nodes.Const)
        >>> method_extractor = Extractor.from_condition(is_method)
        >>> node = astroid.parse(source)
        >>> methods = method_extractor.extract(node)
        >>> list(m.name for m in methods)
        ['one', 'two']
        >>> const_value_extractor = Extractor.from_function(lambda node: node.value if is_const(node) else None)
        >>> const_values = const_value_extractor.extract(node)
        >>> list(const_values)
        [1, 2]
    """

    visitor: Visitor[typing.Optional[T]] = IdentityVisitor()

    def extract(self, node: astroid.nodes.NodeNG) -> typing.Iterator[T]:
        visitor = TreeVisitor[typing.Optional[T], typing.Iterator[typing.Optional[T]]](
            self.visitor
        )
        yield from filter(None, visitor.visit(node))

    @classmethod
    def from_condition(
        cls, condition: Condition, sub_visitor: Visitor[T] = IdentityVisitor()
    ) -> "Extractor[T]":
        visitor = ConditionalVisitor(sub_visitor, condition)
        return cls(visitor)

    @classmethod
    def from_function(
        cls, function: typing.Callable[[astroid.nodes.NodeNG], typing.Optional[T]]
    ):
        visitor = FunctionVisitor(function)
        return cls(visitor)
