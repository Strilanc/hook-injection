from typing import List

from hookinj import gen
from hookinj.circuits.steps._measure_y_transition_round import make_y_transition_round_nesw_xzxz_to_xzzx
from hookinj.circuits.steps._patches import make_xtop_qubit_patch, make_ztop_yboundary_patch


def make_y_memory_experiment_chunks(
        *,
        distance: int,
        memory_rounds: int,
) -> List[gen.Chunk]:
    boundary_patch = make_ztop_yboundary_patch(distance=distance)
    qubit_patch = make_xtop_qubit_patch(distance=distance)
    qubit_obs = gen.PauliString({
        0: 'Y',
        **{q: 'Z' for q in range(1, distance)},
        **{q*1j: 'X' for q in range(1, distance)},
    })

    memory_round = gen.standard_surface_code_chunk(qubit_patch, obs=qubit_obs)
    qubit_to_boundary_round = make_y_transition_round_nesw_xzxz_to_xzzx(distance=distance)
    boundary_round = gen.standard_surface_code_chunk(boundary_patch)
    final_round = gen.standard_surface_code_chunk(
        boundary_patch,
        measure_data_basis={q: 'Z' if q.real + q.imag < distance else 'X' for q in boundary_patch.data_set},
    )

    boundary_rounds = distance // 2
    return [
        final_round.inverted(),
        boundary_round.inverted().with_repetitions(boundary_rounds),
        qubit_to_boundary_round.inverted(),
        memory_round.with_repetitions(memory_rounds),
        qubit_to_boundary_round,
        boundary_round.with_repetitions(boundary_rounds),
        final_round,
    ]


def make_y_memory_transition_chunks_with_magic_before_and_after(
        *,
        distance: int,
        boundary_rounds: int,
        memory_rounds: int,
) -> List[gen.Chunk]:
    boundary_patch = make_ztop_yboundary_patch(distance=distance)
    qubit_patch = make_xtop_qubit_patch(distance=distance)
    qubit_obs = gen.PauliString({
        0: 'Y',
        **{q: 'Z' for q in range(1, distance)},
        **{q*1j: 'X' for q in range(1, distance)},
    })

    memory_round = gen.standard_surface_code_chunk(qubit_patch, obs=qubit_obs)
    qubit_to_boundary_round = make_y_transition_round_nesw_xzxz_to_xzzx(distance=distance)
    boundary_round = gen.standard_surface_code_chunk(boundary_patch)

    return [
        memory_round.magic_init_chunk(),
        memory_round.with_repetitions(memory_rounds),
        qubit_to_boundary_round,
        boundary_round.with_repetitions(boundary_rounds),
        boundary_round.magic_end_chunk(),
    ]


def make_y_measure_chunks_with_magic_before(
        *,
        distance: int,
        boundary_rounds: int,
        memory_rounds: int,
) -> List[gen.Chunk]:
    boundary_patch = make_ztop_yboundary_patch(distance=distance)
    qubit_patch = make_xtop_qubit_patch(distance=distance)
    qubit_obs = gen.PauliString({
        0: 'Y',
        **{q: 'Z' for q in range(1, distance)},
        **{q*1j: 'X' for q in range(1, distance)},
    })

    memory_round = gen.standard_surface_code_chunk(qubit_patch, obs=qubit_obs)
    qubit_to_boundary_round = make_y_transition_round_nesw_xzxz_to_xzzx(distance=distance)
    boundary_round = gen.standard_surface_code_chunk(boundary_patch)
    final_round = gen.standard_surface_code_chunk(
        boundary_patch,
        measure_data_basis={q: 'Z' if q.real + q.imag < distance else 'X' for q in boundary_patch.data_set},
    )

    return [
        memory_round.magic_init_chunk(),
        memory_round.with_repetitions(memory_rounds),
        qubit_to_boundary_round,
        boundary_round.with_repetitions(boundary_rounds),
        final_round,
    ]
