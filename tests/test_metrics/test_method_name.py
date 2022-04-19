import pytest

from sourcery_analytics.metrics.utils import method_name
from sourcery_analytics.validators import InvalidNodeTypeError


@pytest.fixture
def source():
    return """
        import collections #@
        
        def foo(): #@
            return collections.defaultdict(list) #@
    """


def test_neg_statement(nodes):
    with pytest.raises(InvalidNodeTypeError):
        method_name(nodes[0])


def test_ok(nodes):
    result = method_name(nodes[1])
    assert result == "foo"


def test_neg_body(nodes):
    with pytest.raises(InvalidNodeTypeError):
        method_name(nodes[2])
