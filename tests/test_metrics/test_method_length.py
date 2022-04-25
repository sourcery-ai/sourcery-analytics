import pytest

from sourcery_analytics.metrics import method_length
from sourcery_analytics.validators import InvalidNodeTypeError


@pytest.fixture
def source():
    return """
        import collections #@
        
        def ceil(n, k): #@
            if n > k:
                return k
            return n
            
        def nothing(): #@
            pass #@
    """


def test_neg_import(nodes):
    with pytest.raises(InvalidNodeTypeError):
        method_length(nodes[0])


def test_ok_method_1(nodes):
    result = method_length(nodes[1])
    assert result == 3


def test_ok_method_2(nodes):
    result = method_length(nodes[2])
    assert result == 1


def test_neg_body(nodes):
    with pytest.raises(InvalidNodeTypeError):
        method_length(nodes[3])
