from typing import List

from hookinj import gen
from hookinj.circuits.steps._patches import rectangular_unrotated_surface_code_patch


def make_li_injection_rounds(
        *,
        injection_basis: str,
        distance: int = 5,
        memory_rounds: int,
        postselected_rounds: int = 3,
        postselected_diameter: int = 2,
        magic_measurement: bool,
) -> List[gen.Chunk]:
    """Implements the circuit from https://arxiv.org/abs/1410.7808

    To get the exact circuit shown in the paper, use default arguments.

    Args:
        injection_basis: The state to inject (X, Y, or Z).
        distance: The desired patch distance of the prepared logical qubit.
        memory_rounds: The number of rounds to idle in the prepared state, after postselection.
        postselected_rounds: The number of rounds to hold at the smaller distance, with any
            detection events during these rounds resulting in the shot being discarded.
        postselected_diameter: Smaller diameter of patch during postselection rounds.
        magic_measurement: Verify the injected state using a magically noiseless time boundary instead
            of a fault-tolerant time boundary that can be run on hardware.
    """

    assert postselected_diameter >= 2
    assert distance >= postselected_diameter
    assert postselected_rounds >= 1
    assert memory_rounds >= 2
    post_order_X = [None, None, 1, -1, 1j, -1j]
    post_order_Z = [1j, -1j, 1, -1, None, None]

    normal_order_X = [1, 1j, -1j, -1]
    normal_order_Z = [1, -1j, 1j, -1]

    start_patch = rectangular_unrotated_surface_code_patch(
        width=postselected_diameter,
        height=postselected_diameter,
        order_func=lambda q: post_order_X if q.imag % 2 == 0 else post_order_Z,
    )
    full_patch = rectangular_unrotated_surface_code_patch(
        width=distance,
        height=distance,
        order_func=lambda q: normal_order_X if q.imag % 2 == 0 else normal_order_Z,
    )
    obs_xs = gen.PauliString({q: 'X' for q in full_patch.data_set if q.real == 0})
    obs_zs = gen.PauliString({q: 'Z' for q in full_patch.data_set if q.imag == 0})
    assert obs_xs.anticommutes(obs_zs)
    if injection_basis == 'X':
        obs = obs_xs
    elif injection_basis == 'Y':
        obs = obs_xs * obs_zs
    elif injection_basis == 'Z':
        obs = obs_zs
    else:
        raise NotImplementedError(f'{injection_basis=}')
    start_obs = gen.PauliString({q: p for q, p in obs.qubits.items() if q in start_patch.data_set})

    init_round = gen.standard_surface_code_chunk(
        start_patch,
        init_data_basis={
            **{q: 'Z' if q.real > q.imag else 'X' for q in start_patch.data_set},
            0: injection_basis,
        },
        obs=start_obs,
    ).with_flows_postselected(lambda flow: flow.obs_index is None)
    check_round = gen.standard_surface_code_chunk(
        start_patch,
        obs=start_obs,
    ).with_repetitions(postselected_rounds - 1).with_flows_postselected(lambda flow: flow.obs_index is None and flow.start)
    expand_round = gen.standard_surface_code_chunk(
        full_patch,
        init_data_basis={
            q: 'Z' if q.real > q.imag else 'X'
            for q in full_patch.data_set - start_patch.data_set
        },
        obs=obs,
    )

    hold_round = gen.standard_surface_code_chunk(full_patch, obs=obs).with_repetitions(memory_rounds - 2 + magic_measurement)
    if magic_measurement:
        final_round = hold_round.magic_end_chunk()
    elif injection_basis in ['X', 'Z']:
        final_round = gen.standard_surface_code_chunk(
            full_patch,
            measure_data_basis={q: injection_basis for q in full_patch.data_set},
            obs=obs,
        )
    else:
        raise NotImplementedError(f'{magic_measurement=}, {injection_basis=}')

    return [
        init_round,
        check_round,
        expand_round,
        hold_round,
        final_round,
    ]
