from typing import Tuple, Set, AbstractSet, Optional

from hookinj import gen
from hookinj.circuits.steps._patches import make_xtop_qubit_patch, make_ztop_yboundary_patch, DL, DR, UL, UR


def _m_basis(m: complex) -> Optional[str]:
    if m.real % 1 == 0:
        return None
    is_x = int(m.real + m.imag) & 1 == 0
    return 'X' if is_x else 'Z'


def _split_dl_md_ur(ps: AbstractSet[complex]) -> Tuple[Set[complex], Set[complex], Set[complex]]:
    dl = set()
    ur = set()
    md = set()
    for m in ps:
        dst = ur if m.real > m.imag + 1 else md if m.real == m.imag or m.real == m.imag + 1 else dl
        dst.add(m)
    return dl, md, ur


def make_y_transition_round_nesw_xzxz_to_xzzx(
        *,
        distance: int,
        obs_along_bottom: bool = False) -> gen.Chunk:
    start = make_xtop_qubit_patch(distance=distance)
    end = make_ztop_yboundary_patch(distance=distance)
    used = start.used_set | end.used_set

    xs = {q for q in used if _m_basis(q) == 'X'}
    zs = {q for q in used if _m_basis(q) == 'Z'}
    top_row = {q for q in used if q.imag == -0.5}
    right_col = {q for q in used if q.real == distance - 0.5}

    def toward(qs: AbstractSet[complex], delta: complex, sign: int) -> Set[Tuple[complex, complex]]:
        result = set()
        for q in qs:
            if q + delta in used:
                result.add((q, q + delta)[::sign])
        return result

    xs_dl, xs_md, xs_ur = _split_dl_md_ur(xs)
    zs_dl, zs_md, zs_ur = _split_dl_md_ur(zs)

    out = gen.Builder.for_qubits(used)
    out.gate("RX", (xs - right_col) | top_row)
    out.gate("R", (zs - top_row) | right_col)
    out.tick()
    out.gate2('CX', toward(xs - right_col, DL, +1))
    out.gate2('CX', toward(zs - top_row, DL, -1))
    out.tick()
    out.gate2('CX', toward(xs - right_col, DR, +1))
    out.gate2('CX', toward(zs - top_row, UL, -1))
    out.tick()
    out.gate2('CX', toward(xs_ur | xs_md, UL, -1))
    out.gate2('CX', toward(zs_ur, DR, +1))
    out.gate2('XCY', toward(zs_md, DR, +1))
    out.gate2('CX', toward(xs_dl, UL, +1))
    out.gate2('CX', toward(zs_dl, DR, -1))
    out.tick()
    out.gate2('CX', toward(xs_ur, DL, -1))
    out.gate2('CX', toward(zs_ur, DL, +1))
    out.gate2('CX', toward(xs_dl, UR, +1))
    out.gate2('CX', toward(zs_dl, UR, -1))
    out.tick()
    out.gate2('XCY', toward(xs_md - top_row, DL, -1))
    out.tick()
    out.gate('H', [q for q in used if q.real > q.imag])
    out.gate('SQRT_X', [q for q in used if q.real == q.imag and q.real % 1 == 0.5])
    out.tick()
    xms = (xs - top_row) | right_col
    out.measure(xms, basis='X', save_layer='solo')
    out.measure({0}, basis='Y', save_layer='solo')
    out.measure((zs - right_col) | top_row, basis='Z', save_layer='solo')

    flows = []

    # Annotate input stabilizers that get measured.
    for tile in start.tiles:
        m = tile.measurement_qubit
        if m.real == m.imag:
            measurements = [m, m + 1]
        elif m.real == distance - 0.5:
            measurements = [m]
        elif m.imag == -0.5:
            measurements = [m]
        elif m.real > m.imag and tile.basis == 'X':
            measurements = [m - 1j]
        elif m.real > m.imag and tile.basis == 'Z':
            measurements = [m + 1]
        elif m.real < m.imag:
            measurements = [m]
        else:
            raise NotImplementedError(f'{m=!r}')
        flows.append(gen.Flow(
            start=gen.PauliString.from_tile_data(tile),
            center=m,
            measurement_indices=out.tracker.measurement_indices([
                gen.AtLayer(k, layer='solo')
                for k in measurements
            ]),
        ))

    # Annotate output stabilizers that get prepared.
    for tile in end.tiles:
        m = tile.measurement_qubit
        if m == 0.5 + 0.5j:
            measurements = [m, m + 1, m - 1j, m + UL]
        elif m == distance - 0.5 + 0.5j:
            measurements = [m]
        elif m == distance - 1.5 - 0.5j:
            measurements = [m]
        elif m.real == distance - 0.5:
            measurements = [m, m - 1j]
        elif m.imag == -0.5:
            measurements = [m, m + 1]
        elif m.real == m.imag:
            measurements = [m, m + 1, m - 1j]
        else:
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
    if obs_along_bottom:
        flows.append(
            gen.Flow(
                center=0,
                start=gen.PauliString({
                    distance*1j - 1j: 'Y',
                    **{q + distance*1j - 1j: 'Z' for q in range(1, distance)},
                    **{q*1j: 'X' for q in range(distance - 1)},
                }),
                measurement_indices=out.tracker.measurement_indices([
                    gen.AtLayer(m, layer='solo')
                    for m in [0j] + [q for q in xs | zs if q.real <= q.imag]
                ]),
                obs_index=0,
            )
        )
    else:
        flows.append(
            gen.Flow(
                center=0,
                start=gen.PauliString({
                    0: 'Y',
                    **{q: 'Z' for q in range(1, distance)},
                    **{q*1j: 'X' for q in range(1, distance)},
                }),
                measurement_indices=out.tracker.measurement_indices([
                    gen.AtLayer(m, layer='solo')
                    for m in [0j] + list(xms)
                ]),
                obs_index=0,
            )
        )

    return gen.Chunk(
        circuit=out.circuit,
        q2i=out.q2i,
        flows=flows,
    )
