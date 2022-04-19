import pytest

from sourcery_analytics.metrics import method_cognitive_complexity
from sourcery_analytics.metrics.cognitive_complexity import CognitiveComplexityVisitor


class TestMethodCognitiveComplexity:
    @pytest.mark.parametrize(
        "source",
        [
            """
                def one():
                    return 1
            """,
            """
                def sprint(x):
                    print(str(x))
            """,
            """
                def make_foo_cls():
                    class Foo:
                        a: int
                        b: str
                    return Foo
            """,
            """
                def ints(x):
                    yield from range(x)
            """,
        ],
    )
    def test_ok_0(self, node):
        result = method_cognitive_complexity(node)
        assert result == 0

    @pytest.mark.parametrize(
        "source",
        [
            """
                def assess_vibe(vibe_level):
                    if vibe_level > 5:
                        return "good vibe"
            """,
            """
                def suppress_value_error(f):
                    try:
                        f()
                    except ValueError:
                        pass
            """,
            """
                def foreach(xs, f):
                    for x in xs:
                        f(x)
            """,
            """
                def poll(endpoint):
                    while True:
                        print(requests.get(endpoint))
                        time.sleep(5)
            """,
        ],
    )
    def test_ok_1(self, node):
        result = method_cognitive_complexity(node)
        assert result == 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                def ceil(x, y):
                    return y if x > y else x
            """,
            """
                def ceil(x, y):
                    if x < y:
                        return x
                    else:
                        return y
            """,
            """
                def bin(score):
                    if x < 3:
                        return LOW
                    elif x < 7:
                        return MEDIUM
                    return HIGH
            """,
            """
                def my_div(x, y):
                    try:
                        return x / y
                    except ZeroDivisionError:
                        return 0
                    except ValueError:
                        return None
            """,
        ],
    )
    def test_ok_2(self, node):
        result = method_cognitive_complexity(node)
        assert result == 2

    @pytest.mark.parametrize(
        "source",
        [
            """
                def add(x, y):
                    if x:
                        if y:
                            return x + y
            """,
            """
                def filter(xs, cond):
                    for x in xs:
                        if cond(x):
                            yield x
            """,
            """
                def bin(xs):
                    if x < 3:
                        return "BAD"
                    elif x < 7:
                        return "GOOD"
                    else:
                        return "GREAT"
            """,
        ],
    )
    def test_ok_3(self, node):
        result = method_cognitive_complexity(node)
        assert result == 3

    @pytest.mark.parametrize(
        "source",
        [
            """
                def sumOfPrimes(max):
                    total = 0
                    for i in range(1, max):  # + 1
                        for j in range(2, j):  # + 2
                            if i % j == 0:  # + 3
                                break
                            j = j + 1
                        total = total + 1
                        i = i + 1
                    return total
            """
        ],
    )
    def test_ok_sum_of_primes(self, node):
        assert method_cognitive_complexity(node) == 6

    @pytest.mark.parametrize(
        "source",
        [
            """
                def getWords(number):  # + 1
                    if number == 1:  # + 1
                        return "one"
                    elif number == 2:  # + 1
                        return "a couple"
                    elif number == 3:  # + 1
                        return "a few"
                    else:
                        return "lots"  # Total Cognitive Complexity = 4
            """
        ],
    )
    def test_ok_get_words(self, node):
        assert method_cognitive_complexity(node) == 4


class TestCognitiveComplexityVisitor:
    @pytest.fixture(params=[0, 1, 2])
    def nesting(self):
        return 0

    @pytest.fixture
    def visitor(self, nesting):
        return CognitiveComplexityVisitor(0)

    @pytest.mark.parametrize(
        "source",
        [
            """
                if x:  #@
                    foo()
                elif y:  #@
                    bar()
                else:
                    baz()
            """
        ],
    )
    def test_visit_if(self, nesting, nodes, visitor):
        assert visitor.visit(nodes[0]) == nesting
        assert visitor.visit(nodes[1]) == nesting + 1

    @pytest.mark.parametrize(
        "source",
        [
            """
                for x in xs:
                    print(x)
            """,
            """
                while x in xs:
                    print(x)
                    xs.remove(x)
            """,
        ],
    )
    def test_visit_loops(self, nesting, node, visitor):
        assert visitor.visit(node) == nesting

    @pytest.mark.parametrize(
        "source",
        [
            """
                def foo():
                    pass
            """,
            """
                print(5)
            """,
            """
                15 + 5
            """,
        ],
    )
    def test_visit_other(self, node, visitor):
        assert visitor.visit(node) == 0
