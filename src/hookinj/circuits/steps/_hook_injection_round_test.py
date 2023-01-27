import itertools

import pytest

from hookinj.circuits.steps._hook_injection_round import make_hook_injection_round


@pytest.mark.parametrize("d,e", itertools.product(
    range(2, 10),
    [0, 0.5, 1, 1.5],
))
def test_make_injection_round(d: int, e: float):
    make_hook_injection_round(distance=d, exponent=e).verify()
    make_hook_injection_round(distance=d, exponent=e).inverted().verify()
