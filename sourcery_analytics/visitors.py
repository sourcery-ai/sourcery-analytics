"""Classes for handling and recursing into tree structures."""
import abc
import contextlib
import typing

import astroid

from sourcery_analytics.conditions import always, Condition

N = typing.TypeVar("N", bound=astroid.nodes.NodeNG)
P = typing.TypeVar("P")
Q = typing.TypeVar("Q")


class Visitor(abc.ABC, typing.Generic[P]):
    """Abstract visitor class.

    Visitors implement two methods: ``_touch`` and ``_enter``.
    ``_touch`` should return a "fact" about a node, for instance its name or its depth.
    It should *not* directly recurse into the node's children, except where this
    represents part of the "fact" being calculated (see :py:class:`.TreeVisitor`).
    "Facts" which require context, such as depth, can be derived from custom (mutable)
    attributes manipulated in the ``_enter`` method, which, as a context manager,
    should yield after pre-node calculations and before post-node calculations.

    With both these methods implemented, the visitor provides the public ``.visit``
    method to at once enter and calculate over a node.

    Examples:
        >>> class DepthVisitor(Visitor[int]):
        ...     def __init__(self):
        ...         self.depth = 0
        ...     @contextlib.contextmanager
        ...     def _enter(self, node: astroid.nodes.NodeNG):
        ...         self.depth += 1
        ...         yield
        ...         self.depth -= 1
        ...     def visit(self, node: astroid.nodes.NodeNG) -> int:
        ...         return self.depth - 1
    """

    @abc.abstractmethod
    def _touch(self, node: N) -> P:
        """Returns a "fact" about a node."""

    @contextlib.contextmanager
    def _enter(self, node: N):
        """Updates visitor context then yields."""
        yield

    def visit(self, node: N) -> P:
        """Enters the node and returns a fact about it."""
        with self._enter(node):
            return self._touch(node)


class IdentityVisitor(Visitor[astroid.nodes.NodeNG]):
    """No-op visitor, returning the node itself.

    Useful as a default sub-visitor for other visitors.
    """

    def _touch(self, node: N, enter=True) -> N:
        return node


class FunctionVisitor(Visitor[P], typing.Generic[P]):
    """Generic visitor returning the result of its function calculated on the node.

    Examples:
        >>> name_visitor = FunctionVisitor(lambda node: node.__class__.__name__)
        >>> indentation_visitor = FunctionVisitor(lambda node: node.col_offset)
    """

    def __init__(self, function: typing.Callable[[astroid.nodes.NodeNG], P]):
        self.function = function

    def _touch(self, node: astroid.nodes.NodeNG, enter=True) -> P:
        return self.function(node)


class ConditionalVisitor(Visitor[typing.Optional[P]], typing.Generic[P]):
    """A visitor returning the result of its sub-visitor when its condition is True, and None otherwise.

    By default, this visitor will unconditionally return the node itself.

    Attributes:
        sub_visitor: a Visitor to optionally return the result from.
        condition: a Condition describing when to return the result.

    Examples:
        >>> from sourcery_analytics.conditions import is_type
        >>> method_visitor = ConditionalVisitor(condition=is_type(astroid.nodes.FunctionDef))
        >>> method = astroid.extract_node("def foo(): pass")
        >>> method_visitor.visit(method).name
        'foo'
        >>> binop = astroid.extract_node("a + b")
        >>> method_visitor.visit(binop) is None
        True

    See Also:
        * :py:class:`.Extractor`
    """

    def __init__(
        self,
        sub_visitor: Visitor[P] = IdentityVisitor(),
        condition: Condition = always,
    ):
        self.sub_visitor = sub_visitor
        self.condition = condition

    @contextlib.contextmanager
    def _enter(self, node: astroid.nodes.NodeNG):
        with self.sub_visitor._enter(node):
            yield

    def _touch(self, node: astroid.nodes.NodeNG, enter=True) -> typing.Optional[P]:
        return self.sub_visitor._touch(node) if self.condition(node) else None


class CompoundVisitor(Visitor[Q], typing.Generic[P, Q]):
    """Combines a collection of other visitors into a single visitor, handling context and collection of the results.

    This is most useful when you need a single sub-visitor for some other visitor.

    Examples:
        Collect the name and indentation of every sub-node in a tree:

        >>> name_visitor = FunctionVisitor(lambda node: node.__class__.__name__)
        >>> line_visitor = FunctionVisitor(lambda node: node.lineno)
        >>> name_line_visitor = CompoundVisitor(name_visitor, line_visitor)
        >>> every_node_visitor = TreeVisitor(name_line_visitor, collector=list)
        >>> source = '''
        ...     def one():
        ...         return 1
        ... '''
        >>> from sourcery_analytics.utils import clean_source
        >>> node = astroid.parse(clean_source(source))
        >>> every_node_visitor.visit(node)
        [('Module', 0), ('FunctionDef', 1), ('Arguments', None), ('Return', 2), ('Const', 2)]
    """

    def __init__(
        self,
        *visitors: Visitor[P],
        collector: typing.Callable[[typing.Iterable[P]], Q] = tuple  # type: ignore
    ):
        self.visitors = visitors
        self.collector = collector

    @contextlib.contextmanager
    def _enter(self, node: astroid.nodes.NodeNG):
        with contextlib.ExitStack() as stack:
            for visitor in self.visitors:
                stack.enter_context(visitor._enter(node))
            yield

    def _touch(self, node: astroid.nodes.NodeNG, enter=True) -> Q:
        return self.collector((visitor._touch(node) for visitor in self.visitors))


class TreeVisitor(Visitor, typing.Generic[P, Q]):
    """Visitor with a sub-visitor which collects the result of that sub-visitor applied to every sub-node of a node.

    By default, returns an iterable of every sub-node of a node.
    The type parameters indicate the expected output of the sub-visitor and
    the output of the tree visitor respectively (as handled by the collector).

    Examples:
        >>> name_visitor = FunctionVisitor(lambda node: node.__class__.__name__)
        >>> every_name_visitor = TreeVisitor(name_visitor, list)
        >>> source = "x + y"
        >>> node = astroid.extract_node(source)
        >>> every_name_visitor.visit(node)
        ['BinOp', 'Name', 'Name']
    """

    def __init__(
        self,
        sub_visitor: Visitor[P] = IdentityVisitor(),
        collector: typing.Callable[[typing.Iterator[P]], Q] = iter,  # type: ignore
    ):
        self.sub_visitor = sub_visitor
        self.collector = collector

    @contextlib.contextmanager
    def _enter(self, node: astroid.nodes.NodeNG):
        with self.sub_visitor._enter(node):
            yield

    def _visit(self, node: astroid.nodes.NodeNG):
        yield self.sub_visitor._touch(node)
        for child in node.get_children():
            with self._enter(child):
                yield from self._visit(child)

    def _touch(self, node: astroid.nodes.NodeNG) -> Q:
        return self.collector(self._visit(node))
