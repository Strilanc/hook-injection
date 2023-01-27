from typing import List, Optional

from hookinj import gen


BASE_ORDER = 'XZZX'
TWEAKED_BASE_ORDER = 'ZXXZ'


def unrotated_xzzx_measure_order(q: complex, tweaked: bool) -> Optional[List[complex]]:
    if q.real % 2 == q.imag % 2:
        return None
    if not tweaked:
        return [-1, -1j, 1j, 1]
    return [-1j, 1, -1, 1j]


def xzzx_equiv_basis(q: complex, raw_data_basis: str) -> str:
    if q.real % 2 != q.imag % 2:
        # Measure qubit.
        return 'X'
    if q.imag % 2 == 1:
        return 'X' if raw_data_basis == 'Z' else 'Z'
    return raw_data_basis


def zz_inject_xzzx_round(
        *,
        next_d: int,
        prev_d: int = None,
        basis: str,
        postselect: bool = False,
        tweaked: bool = False,
) -> gen.Chunk:
    distance = max(next_d, prev_d)
    used_qubits = {
        x + 1j*y
        for x in range(2*distance - 1)
        for y in range(2*distance - 1)
    }
    measure_qubits = {
        m
        for m in used_qubits
        if unrotated_xzzx_measure_order(m, tweaked=tweaked) is not None
    }
    data_qubits = used_qubits - measure_qubits

    obs_xs = gen.PauliString({q: 'X' for q in data_qubits if q.real == 0})
    obs_zs = gen.PauliString({q: 'Z' for q in data_qubits if q.imag == 0})
    assert obs_xs.anticommutes(obs_zs)
    if basis == 'Y':
        obs = obs_xs * obs_zs
    elif basis == 'X':
        obs = obs_xs
    else:
        raise NotImplementedError(f'{basis=}')

    init_qubits = {}
    qubits_to_measure = {}
    for m in measure_qubits:
        init_qubits[m] = 'X'
        qubits_to_measure[m] = 'X'
    for q in data_qubits:
        if max(q.imag, q.real) >= prev_d * 2 - 1:
            if tweaked:
                raw_basis = 'X' if q.real <= max(2, q.imag) else 'Z'
            elif prev_d == 0:
                raw_basis = 'X' if q.real <= 2 else 'Z'
            else:
                raw_basis = 'X' if q.imag >= prev_d * 2 - 1 else 'Z'
            init_qubits[q] = xzzx_equiv_basis(q, raw_basis)
        if max(q.imag, q.real) >= next_d * 2 - 1:
            if next_d == 0:
                raw_basis = 'X'
            elif tweaked:
                raw_basis = 'X' if q.real <= max(2, q.imag) else 'Z'
            else:
                raw_basis = 'X' if q.imag >= next_d * 2 - 1 else 'Z'
            qubits_to_measure[q] = xzzx_equiv_basis(q, raw_basis)

    builder = gen.Builder.for_qubits(used_qubits)
    for b in 'XYZ':
        builder.gate(f'R{b}', [q for q in init_qubits if init_qubits[q] == b])
    builder.tick()
    if basis == 'Y' and prev_d == 0:
        builder.gate2('SQRT_ZZ', [(0, 2)])
        builder.tick()
    base_order = TWEAKED_BASE_ORDER if tweaked else BASE_ORDER
    for layer in range(4):
        pairs = []
        for m in measure_qubits:
            order = unrotated_xzzx_measure_order(m, tweaked)
            d = m + order[layer]
            if d in used_qubits:
                pairs.append((m, d))
        builder.gate2('C' + base_order[layer], pairs)
        builder.tick()
    for b in 'XYZ':
        builder.measure([q for q in qubits_to_measure if qubits_to_measure[q] == b], basis=b, save_layer='solo')

    flows = []
    discarded_inputs = []
    for m in measure_qubits:
        full_stabilizer = gen.PauliString({
            m + delta: basis
            for delta, basis in zip(unrotated_xzzx_measure_order(m, tweaked), base_order)
            if m + delta in data_qubits
        })
        start = gen.PauliString({
            q: b
            for q, b in full_stabilizer.qubits.items()
            if q not in init_qubits
        })

        if all(init_qubits.get(q, b) == b for q, b in full_stabilizer.qubits.items()):
            flows.append(gen.Flow(
                start=start,
                measurement_indices=builder.tracker.measurement_indices([
                    gen.AtLayer(m, 'solo'),
                ]),
                center=m,
                postselect=postselect,
            ))
        else:
            discarded_inputs.append(start)

        if all(qubits_to_measure.get(q, b) == b for q, b in full_stabilizer.qubits.items()):
            flows.append(gen.Flow(
                end=gen.PauliString({
                    q: b
                    for q, b in full_stabilizer.qubits.items()
                    if q not in qubits_to_measure
                }),
                measurement_indices=builder.tracker.measurement_indices([
                    gen.AtLayer(q, 'solo')
                    for q in full_stabilizer.qubits.keys() | {m}
                    if q in qubits_to_measure
                ]),
                center=m,
            ))

    flows.append(gen.Flow(
        start=gen.PauliString({q: b for q, b in obs.qubits.items() if q not in init_qubits}),
        end=gen.PauliString({q: b for q, b in obs.qubits.items() if q not in qubits_to_measure}),
        measurement_indices=builder.tracker.measurement_indices([
            gen.AtLayer(q, 'solo') for q in obs.qubits.keys()
            if q in qubits_to_measure
        ]),
        center=0,
        obs_index=0,
    ))

    return gen.Chunk(
        circuit=builder.circuit,
        q2i=builder.q2i,
        flows=flows,
        discarded_inputs=discarded_inputs,
    )


def make_zz_injection(
        *,
        injection_basis: str,
        distance: int = 5,
        memory_rounds: int,
        postselected_rounds: int = 3,
        postselected_diameter: int = 2,
        magic_measurement: bool,
        tweaked: bool = False,
) -> List[gen.Chunk]:
    """From https://arxiv.org/abs/2109.02677 ."""
    assert postselected_diameter >= 2
    assert distance >= postselected_diameter
    assert postselected_rounds >= 1
    assert memory_rounds >= 2

    inject = zz_inject_xzzx_round(
        prev_d=0,
        next_d=postselected_diameter,
        basis=injection_basis,
        postselect=True,
        tweaked=tweaked,
    )
    postselect = zz_inject_xzzx_round(
        prev_d=postselected_diameter,
        next_d=postselected_diameter,
        basis=injection_basis,
        postselect=True,
        tweaked=tweaked,
    )
    transition = zz_inject_xzzx_round(
        prev_d=postselected_diameter,
        next_d=distance,
        basis=injection_basis,
        tweaked=tweaked,
    )
    idle = zz_inject_xzzx_round(
        prev_d=distance,
        next_d=distance,
        basis=injection_basis,
        tweaked=tweaked,
    )
    if magic_measurement:
        end = idle.magic_end_chunk()
    else:
        end = zz_inject_xzzx_round(
            prev_d=distance,
            next_d=0,
            basis=injection_basis,
            tweaked=tweaked,
        )

    return [
        inject,
        postselect.with_repetitions(postselected_rounds - 1),
        transition,
        idle.with_repetitions(memory_rounds - 2),
        end,
    ]
