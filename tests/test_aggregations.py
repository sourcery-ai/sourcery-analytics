import functools
import itertools
import operator

import pytest


@pytest.mark.parametrize(
    "xs, expected",
    [
        ([1, 2, 3], 2.0),
        (iter([1, 2, 3]), 2.0),
    ],
)
def test_mean(xs, expected):
    total_iter, count_iter = itertools.tee(xs)
    # sum doesn't use __add__, so use operator here instead
    total_ = functools.reduce(operator.add, total_iter)
    count = len(list(count_iter))
    assert total_ / count == expected
