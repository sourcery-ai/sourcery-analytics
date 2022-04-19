"""Functions that don't fit anywhere else."""
import textwrap
import typing

T = typing.TypeVar("T")


def clean_source(source_str: str) -> str:
    """Remove whitespace surrounding a source code string.

    Examples:
        >>> source = '''
        ...
        ...     def example():
        ...         return "have a nice day"
        ... '''
        >>> clean_source(source)
        'def example():\\n    return "have a nice day"'
    """
    return textwrap.dedent(source_str).strip()
