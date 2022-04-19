import pytest

from sourcery_analytics.metrics import method_working_memory
from sourcery_analytics.metrics.working_memory import WorkingMemoryVisitor, get_names
from sourcery_analytics.utils import clean_source


class TestMethodWorkingMemory:
    @pytest.mark.parametrize(
        "source",
        [
            """
                def skip():
                    pass
            """,
            """
                def zero():
                    return 0
            """,
        ],
    )
    def test_0(self, node):
        assert method_working_memory(node) == 0

    @pytest.mark.parametrize(
        "source",
        [
            """
                def identity(x):
                    return x
            """,
            """
                def add_one(x):
                    return x + 1
            """,
            """
                def add_one_badly(x):
                    x = x + 1
                    return x
            """,
            """
                def get_egg_priority(egg):
                    return {
                        "easter": 0,
                        "chicken": 1,
                        "goose": 2
                    }[egg]
            """,
        ],
    )
    def test_1(self, node):
        assert method_working_memory(node) == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                def add(x, y):
                    return x + y
            """,
            """
                def check(thing):
                    if thing:
                        return thing
                    return None
            """,
            """
                def display(s):
                    print(s)
            """,
        ],
        ids=clean_source,
    )
    def test_2(self, node):
        assert method_working_memory(node) == 2

    @pytest.mark.parametrize(
        "source",
        [
            """
                def call_conditional(f, condition):
                    if condition:
                        f()
            """,
            """
                def loop(xs, f):
                    for x in xs:
                        yield f(x)
            """,
        ],
        ids=clean_source,
    )
    def test_3(self, node):
        assert method_working_memory(node) == 3


class TestWorkingMemoryVisitor:
    @pytest.fixture
    def condition_penalty(self):
        return 0

    @pytest.fixture
    def visitor(self, condition_penalty):
        return WorkingMemoryVisitor(_condition_penalty=condition_penalty)

    @pytest.mark.parametrize(
        "source, expected",
        [
            ("if x: pass", 1),
            ("if x and y: pass", 2),
            ("if x and y: z = x + y", 2),
        ],
    )
    def test_visit_if(self, visitor, node, expected):
        assert visitor.visit(node) == expected

    @pytest.mark.parametrize(
        "source, expected",
        [
            ("for x in xs: ...", 2),
            ("for t in zip(xs, ys): ...", 4),
            ("for x, y in zip(xs, ys): ...", 5),
        ],
    )
    def test_visit_for(self, visitor, node, expected):
        assert visitor.visit(node) == expected

    @pytest.mark.parametrize(
        "source",
        [
            "class Foo: ...",
            "def foo(): ...",
        ],
    )
    def test_visit_defs(self, visitor, node):
        assert visitor.visit(node) == 0

    @pytest.mark.parametrize(
        "source, expected",
        [
            ("a = max(x, y)", 4),
            ("a = max(x, y)", 4),
            ("pass", 0),
        ],
    )
    def test_visit_statement(self, visitor, node, expected):
        assert visitor.visit(node) == expected

    @pytest.mark.parametrize(
        "source",
        [
            "x + y",
            "zip(xs, ys)",
            "print(self.radiation_level)",
            "a and b",
        ],
    )
    def test_visit_other(self, visitor, node):
        assert visitor.visit(node) == 0


@pytest.mark.parametrize(
    "source, expected",
    [
        ("x", {"x"}),
        ("x, y", {"x", "y"}),
        ("a + b", {"a", "b"}),
        ("self.x", {"self", "x"}),
        ("self.point.x", {"self", "point", "x"}),
        (
            "for x, y in zip(xs, ys): print(x, y)",
            {"xs", "ys", "x", "y", "zip", "print"},
        ),
    ],
)
def test_get_names(node, expected):
    assert get_names(node) == expected
