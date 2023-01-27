import pytest

from hookinj.circuits.steps._measure_y_transition_round import \
    make_y_transition_round_nesw_xzxz_to_xzzx


@pytest.mark.parametrize("d", range(2, 10))
def test_make_y_transition_round_nesw_xzxz_to_xzzx(d: int):
    make_y_transition_round_nesw_xzxz_to_xzzx(distance=d).verify()
    make_y_transition_round_nesw_xzxz_to_xzzx(distance=d).inverted().verify()
    make_y_transition_round_nesw_xzxz_to_xzzx(distance=d, obs_along_bottom=True).verify()
    make_y_transition_round_nesw_xzxz_to_xzzx(distance=d, obs_along_bottom=True).inverted().verify()
