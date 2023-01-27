from typing import List

from hookinj import gen
from hookinj.circuits.steps._patches import make_xtop_qubit_patch


def make_xz_memory_experiment_chunks(
        *,
        distance: int,
        basis: str,
        memory_rounds: int,
) -> List[gen.Chunk]:
    qubit_patch = make_xtop_qubit_patch(distance=distance)
    xs = {q for q in qubit_patch.data_set if q.real == 0}
    zs = {q for q in qubit_patch.data_set if q.imag == 0}
    assert len(xs & zs) % 2 == 1
    obs = gen.PauliString({q: basis for q in (xs if basis == 'X' else zs)})
    assert memory_rounds > 0
    if memory_rounds == 1:
        return [
            gen.standard_surface_code_chunk(
                qubit_patch,
                init_data_basis=basis,
                measure_data_basis=basis,
                obs=obs)
        ]

    return [
        gen.standard_surface_code_chunk(
            qubit_patch,
            init_data_basis=basis,
            obs=obs,
        ),
        gen.standard_surface_code_chunk(
            qubit_patch,
            obs=obs,
        ).with_repetitions(memory_rounds - 2),
        gen.standard_surface_code_chunk(
            qubit_patch,
            measure_data_basis=basis,
            obs=obs,
        ),
    ]
