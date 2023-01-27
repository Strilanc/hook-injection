from typing import List

from hookinj import gen
from hookinj.circuits._y_memory_circuit import make_y_memory_experiment_chunks
from hookinj.circuits.steps._hook_injection_round import make_hook_injection_round
from hookinj.circuits.steps._patches import make_xtop_qubit_patch


def make_hook_injection_circuit(
        *,
        distance: int,
        postselected_rounds: int,
        postselected_diameter: int,
        memory_rounds: int,
        injection_basis: str,
        magic_measurement: bool,
        start_full: bool,
) -> List[gen.Chunk]:
    postselect_detector_func = lambda x, y, t: abs(x) <= postselected_diameter and abs(y) <= postselected_diameter and t < postselected_rounds

    assert postselected_rounds >= 1
    assert memory_rounds >= 2
    start_distance = distance if start_full else min(postselected_diameter, distance)
    end_distance = distance
    start_patch = make_xtop_qubit_patch(distance=start_distance).with_opposite_order()
    end_patch = make_xtop_qubit_patch(distance=end_distance).with_opposite_order()

    obs_xs = gen.PauliString({q: 'X' for q in end_patch.data_set if q.real == 0})
    obs_zs = gen.PauliString({q: 'Z' for q in end_patch.data_set if q.imag == 0})
    assert obs_xs.anticommutes(obs_zs)
    if injection_basis == 'X':
        end_obs = obs_xs
    elif injection_basis == 'Y':
        end_obs = obs_xs * obs_zs
    else:
        raise NotImplementedError(f'{injection_basis=}')
    start_obs = gen.PauliString({q: b for q, b in end_obs.qubits.items() if q in start_patch.data_set})

    injection_round = make_hook_injection_round(exponent=0.5 if injection_basis == 'Y' else 0, distance=start_distance)
    start_memory_round = gen.standard_surface_code_chunk(start_patch, obs=start_obs)
    transition_round = gen.standard_surface_code_chunk(end_patch, obs=end_obs, init_data_basis={
        q: 'X' if q.real <= q.imag or q == 1 else 'Z' for q in end_patch.data_set - start_patch.data_set
    })
    end_memory_round = gen.standard_surface_code_chunk(end_patch, obs=end_obs)

    chunks = []
    chunks.append(injection_round.with_flows_postselected(lambda flow: postselect_detector_func(flow.center.real, flow.center.imag, 0)))
    for k in range(1, postselected_rounds):
        t = len(chunks)
        chunks.append(start_memory_round.with_flows_postselected(lambda flow: not flow.end and postselect_detector_func(flow.center.real, flow.center.imag, t)))
    chunks.append(transition_round)
    chunks.append(end_memory_round.with_repetitions(memory_rounds - 2 + (magic_measurement or injection_basis == 'Y')))

    if magic_measurement:
        chunks.append(end_memory_round.magic_end_chunk())
    elif injection_basis == 'Y':
        chunks.extend(make_y_memory_experiment_chunks(
            distance=end_distance,
            memory_rounds=0,
        )[-3:])
    else:
        chunks.append(gen.standard_surface_code_chunk(end_patch, obs=end_obs, measure_data_basis=injection_basis))

    return chunks
