import astroid
import pytest

from sourcery_analytics import analyze_methods, analyze
from sourcery_analytics.metrics import (
    method_length,
    method_cognitive_complexity,
    statement_count,
    cyclomatic_complexity,
    node_type_name,
)
from sourcery_analytics.metrics.aggregations import total, average, peak
from sourcery_analytics.metrics.compounders import name_metrics, tuple_metrics
from sourcery_analytics.metrics.cyclomatic_complexity import total_cyclomatic_complexity
from sourcery_analytics.metrics.method_length import total_statement_count


class TestAnalyzeMethods:
    @pytest.mark.parametrize(
        "item",
        ["def foo(): pass", astroid.parse("def foo(): pass")],
    )
    @pytest.mark.parametrize(
        "metrics",
        [None, [method_length], [method_length, method_cognitive_complexity]],
    )
    @pytest.mark.parametrize(
        "compounder",
        [name_metrics, tuple_metrics],
    )
    @pytest.mark.parametrize(
        "aggregation",
        [list, tuple, total, average, peak],
    )
    def test_analyze_methods_options(self, item, metrics, compounder, aggregation):
        """Check analysis doesn't fail for combinations of inputs."""
        analyze_methods(
            item, metrics=metrics, compounder=compounder, aggregation=aggregation
        )

    def test_analyze_methods_path(self, tmp_path):
        """Check analysis doesn't fail for a path."""
        tmp_file = tmp_path / "file.py"
        tmp_file.write_text("""def foo(): pass""")
        analyze_methods(tmp_file)

    @pytest.mark.parametrize(
        "source, metrics, expected",
        [
            ("def foo(): pass", [method_length], [(1,)]),
            (
                """
                    def maybe_add(x, y):
                        if x:
                            if y:
                                return x + y
                            
                """,
                [method_length, method_cognitive_complexity],
                [(3, 3)],
            ),
            (
                """
                    def yes():
                        return True
                    def no():
                        return False
                """,
                None,
                [(".yes", 1, 0, 0, 0), (".no", 1, 0, 0, 0)],
            ),
            ("if x: y", None, []),
        ],
    )
    def test_analyze_methods_result(self, cleaned_source, metrics, expected):
        """Check the analysis produces the correct result."""
        analysis = analyze_methods(
            cleaned_source, metrics=metrics, compounder=tuple_metrics
        )
        assert analysis == expected


class TestAnalyze:
    @pytest.mark.parametrize(
        "source",
        [
            """
                def foo():  #@
                    pass  #@
            """,
            """
                if xs:  #@
                    do_y()  #@
            """,
            """
                for foo in foos:  #@
                    if c:  #@
                        whatever()  #@
            """,
        ],
    )
    @pytest.mark.parametrize(
        "metrics",
        [
            [statement_count, cyclomatic_complexity, node_type_name],
        ],
    )
    @pytest.mark.parametrize("compounder", [name_metrics, tuple_metrics])
    @pytest.mark.parametrize("aggregation", [list, tuple, total, peak, average])
    def test_analyze_options(self, nodes, metrics, compounder, aggregation):
        """Check analyze works with combinations of options."""
        analyze(nodes, metrics, compounder, aggregation)

    @pytest.mark.parametrize(
        "source, metrics, expected",
        [
            (
                """
                    if x:  #@
                        y  #@
                """,
                [statement_count],
                [(1,), (0,)],
            ),
            (
                """
                    if x:
                        thing()
                    elif y:
                        other_thing()
                """,
                [total_statement_count, total_cyclomatic_complexity],
                [(4, 2)],
            ),
        ],
    )
    def test_analyze_results(self, nodes, metrics, expected):
        """Check analyze produces the correct results."""
        analysis = analyze(nodes, metrics, compounder=tuple_metrics)
        assert analysis == expected
