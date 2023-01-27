from typing import AbstractSet, Set, Tuple

from hookinj import gen
from hookinj.circuits.steps._patches import make_xtop_qubit_patch, DL, UR, UL, DR


def make_hook_injection_round(*, exponent: float, distance: int) -> gen.Chunk:
    patch = make_xtop_qubit_patch(distance=distance)
    xs = {q for q in patch.measure_set if gen.checkerboard_basis(q) == 'X'}
    zs = {q for q in patch.measure_set if gen.checkerboard_basis(q) == 'Z'}
    mid = {q for q in patch.measure_set if q.real == q.imag}
    arbitrary_rotation_gate = {
        0: 'I',
        0.5: 'S',
        1: 'Z',
        1.5: 'S_DAG',
    }[exponent % 2]

    def toward(qs: AbstractSet[complex], delta: complex, sign: int) -> Set[Tuple[complex, complex]]:
        result = set()
        for q in qs:
            if q + delta in patch.used_set:
                result.add((q, q + delta)[::sign])
        return result

    data_basis = {q: 'X' if q.real <= q.imag or q == 1 else 'Z' for q in patch.data_set}

    out = gen.Builder.for_qubits(patch.used_set)
    x_init = xs | {q for q, b in data_basis.items() if b == 'X'}
    z_init = zs | {q for q, b in data_basis.items() if b == 'Z'}
    out.gate("RX", x_init)
    out.gate("R", z_init)
    out.tick()
    out.gate2('CX', [(a, b) for a, b in toward(xs, UR, +1) if a not in z_init and b not in x_init])
    out.gate2('CX', [(a, b) for a, b in toward(zs, UR, -1) if a not in z_init and b not in x_init])
    out.tick()
    out.gate2('CX', toward(xs, UL, +1))
    out.gate2('CX', toward(zs - mid, DR, -1))
    out.gate2('CX', toward(mid, UL, -1))
    out.tick()
    out.gate(arbitrary_rotation_gate, [0.5 + 0.5j])  # injection
    out.tick()
    out.gate2('CX', toward(xs, DR, +1))
    out.gate2('CX', toward(zs - mid, UL, -1))
    out.gate2('CX', toward(mid, DR, -1))
    out.tick()
    out.gate2('CX', toward(xs, DL, +1))
    out.gate2('CX', toward(zs, DL, -1))
    out.tick()
    out.measure(xs, basis='X', save_layer='solo')
    out.measure(zs, basis='Z', save_layer='solo')

    flows = []

    # Annotate data-initialized stabilizers.
    for tile in patch.tiles:
        m = tile.measurement_qubit
        if all(q is None or data_basis[q] == b for q, b in zip(tile.ordered_data_qubits, tile.bases)):
            measurements = [m]
        else:
            continue
        flows.append(gen.Flow(
            center=m,
            measurement_indices=out.tracker.measurement_indices([
                gen.AtLayer(k, layer='solo')
                for k in measurements
            ]),
        ))

    # Annotate output stabilizers that get prepared.
    for tile in patch.tiles:
        m = tile.measurement_qubit
        measurements = [m]
        flows.append(gen.Flow(
            end=gen.PauliString.from_tile_data(tile),
            center=m,
            measurement_indices=out.tracker.measurement_indices([
                gen.AtLayer(k, layer='solo')
                for k in measurements
            ]),
        ))

    # Annotate how observable flows through the system.
    obs_xs = gen.PauliString({q: 'X' for q in patch.data_set if q.real == 0})
    obs_zs = gen.PauliString({q: 'Z' for q in patch.data_set if q.imag == 0})
    assert obs_xs.anticommutes(obs_zs)
    if exponent % 1 == 0:
        obs = obs_xs
    else:
        obs = obs_xs * obs_zs
    flows.append(
        gen.Flow(
            center=0,
            end=obs,
            obs_index=0,
        )
    )

    return gen.Chunk(
        circuit=out.circuit,
        q2i=out.q2i,
        flows=flows,
    )
