"""True or False statements about nodes."""
import typing

import astroid.nodes

Condition = typing.Callable[[astroid.nodes.NodeNG], bool]


def always(_node: astroid.nodes.NodeNG) -> bool:
    """Always True for any node.

    Useful as a default fallback.
    """
    return True


def is_type(*t: typing.Type[astroid.nodes.NodeNG]) -> Condition:
    """Construct a Condition based on the type of the node.

    Examples:
        >>> is_method = is_type(astroid.nodes.FunctionDef)
        >>> module = astroid.parse("def foo(): pass")
        >>> is_method(module)
        False
        >>> is_method(module.body[0])
        True
    """

    def _is_type(node: astroid.nodes.NodeNG):
        return isinstance(node, t)

    return _is_type


def is_elif(node: astroid.nodes.NodeNG) -> bool:
    """True if the node corresponds to an `elif` statement.

    Python parsers treat if.. elif.. statements as a nested if.. else: if.. statement,
    so detecting elifs is not trivial. Here, we assert that an if statement is an elif
    if its parent is an if, it is the first statement of the parent's else condition,
    and the column offset is the same.

    Note:
         Because of the final condition, this will not work if the node is
         constructed manually.

    From an execution perspective, this distinction isn't relevant, but from a code
    quality perspective, (especially for cognitive complexity) it is important.
    """
    return (
        isinstance(node, astroid.nodes.If)
        and isinstance(node.parent, astroid.nodes.If)
        and node.parent.orelse
        and node.parent.orelse[0] is node
        and node.col_offset == node.parent.col_offset
    )


is_method = is_type(astroid.nodes.FunctionDef)
is_const = is_type(astroid.nodes.Const)
is_name = is_type(astroid.nodes.Name)
