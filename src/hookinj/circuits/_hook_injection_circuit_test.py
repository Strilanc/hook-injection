import itertools
from typing import Tuple

import pytest
import stim

from hookinj import gen
from hookinj._make_circuit import make_circuit


def count_d1_and_d2_errors(circuit: stim.Circuit) -> Tuple[int, int]:
    dem = circuit.detector_error_model()

    has_l0 = set()
    not_has_l0 = set()
    for inst in dem.flattened():
        if inst.type == "error":
            targets = inst.targets_copy()
            has_logical = sum(t.is_logical_observable_id() for t in targets) % 2 == 1
            detectors = set()
            for t in targets:
                if t.is_relative_detector_id():
                    if t.val in detectors:
                        detectors.remove(t.val)
                    else:
                        detectors.add(t.val)
            if has_logical:
                dst = has_l0
            else:
                dst = not_has_l0
            dst.add(frozenset(detectors))
    d2_sets = has_l0 & not_has_l0
    dem2 = stim.DetectorErrorModel()
    for e in d2_sets:
        dem2.append("error", 0.125, [stim.DemTarget.relative_detector_id(d) for d in sorted(e)])
        dem2.append("error", 0.125, [stim.target_logical_observable_id(0)] + [stim.DemTarget.relative_detector_id(d) for d in sorted(e)])

    d1_errs, = circuit.explain_detector_error_model_errors(dem_filter=stim.DetectorErrorModel("""
        error(0.1) L0
    """))
    num_d1 = len(d1_errs.circuit_error_locations)
    num_d2 = sum(len(e.circuit_error_locations) for e in circuit.explain_detector_error_model_errors(dem_filter=dem2))
    return num_d1, num_d2


@pytest.mark.parametrize("basis,distance", itertools.product(
    ['hook_inject_X', 'hook_inject_Y'],
    range(2, 9),
))
def test_make_injection_circuit(basis: str, distance: int):
    circuit = make_circuit(
        basis=basis,
        distance=distance,
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        postselected_rounds=3,
        postselected_diameter=4,
        memory_rounds=6,
        verify_chunks=True,
    )

    dem = circuit.detector_error_model(decompose_errors=True, block_decomposition_from_introducing_remnant_edges=True)
    assert dem is not None

    actual_distance = len(circuit.shortest_graphlike_error())
    assert actual_distance == 1

    if distance == 2:
        expected_d1_terms = 5
    elif 'Y' in basis:
        expected_d1_terms = 4
    else:
        expected_d1_terms = 3
    if 'Y' in basis:
        if distance == 2:
            expected_d2_errors = 1872
        elif distance == 3:
            expected_d2_errors = 225
        else:
            expected_d2_errors = 203
    else:
        if distance == 2:
            expected_d2_errors = 1222
        elif distance == 3:
            expected_d2_errors = 212
        else:
            expected_d2_errors = 190
    num_d1, num_d2 = count_d1_and_d2_errors(circuit)
    assert num_d1 == expected_d1_terms
    assert num_d2 == expected_d2_errors


def test_hook_injection_circuit_same_post_select_regardless_of_basis_and_verification():
    circuits = [make_circuit(
        basis=basis,
        distance=4,
        noise=gen.NoiseModel.si1000(1e-3),
        postselected_rounds=2,
        postselected_diameter=3,
        memory_rounds=6,
    ) for basis in ["hook_inject_X", "hook_inject_Y", "hook_inject_Y_magic_verify", "hook_inject_X_magic_verify"]]
    counts = [
        sum(inst.name == "DETECTOR" and 999 in inst.gate_args_copy() for inst in c.flattened())
        for c in circuits
    ]
    assert len(set(counts)) == 1


def test_hook_injection_circuit_exact():
    assert make_circuit(
        basis="hook_inject_X",
        distance=3,
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        postselected_rounds=2,
        postselected_diameter=2,
        memory_rounds=6,
    ) == stim.Circuit("""
        QUBIT_COORDS(0, 0) 0
        QUBIT_COORDS(0, 1) 1
        QUBIT_COORDS(0, 2) 2
        QUBIT_COORDS(1, 0) 3
        QUBIT_COORDS(1, 1) 4
        QUBIT_COORDS(1, 2) 5
        QUBIT_COORDS(2, 0) 6
        QUBIT_COORDS(2, 1) 7
        QUBIT_COORDS(2, 2) 8
        QUBIT_COORDS(-0.5, 1.5) 9
        QUBIT_COORDS(0.5, -0.5) 10
        QUBIT_COORDS(0.5, 0.5) 11
        QUBIT_COORDS(0.5, 1.5) 12
        QUBIT_COORDS(1.5, 0.5) 13
        QUBIT_COORDS(1.5, 1.5) 14
        QUBIT_COORDS(1.5, 2.5) 15
        QUBIT_COORDS(2.5, 0.5) 16
        R 0 1 3 4 10 12 11
        X_ERROR(0.001) 0 1 3 4 10 12 11
        DEPOLARIZE1(0.001) 2 5 6 7 8 9 13 14 15 16
        TICK
        H 0 3 4 10 11 12
        DEPOLARIZE1(0.001) 0 3 4 10 11 12 1 2 5 6 7 8 9 13 14 15 16
        TICK
        CZ 3 11
        DEPOLARIZE2(0.001) 3 11
        DEPOLARIZE1(0.001) 0 1 2 4 5 6 7 8 9 10 12 13 14 15 16
        TICK
        CZ 0 11 1 12
        DEPOLARIZE2(0.001) 0 11 1 12
        DEPOLARIZE1(0.001) 2 3 4 5 6 7 8 9 10 13 14 15 16
        TICK
        H 0 1 3 12
        DEPOLARIZE1(0.001) 0 1 3 12 2 4 5 6 7 8 9 10 11 13 14 15 16
        TICK
        CZ 3 10 4 11
        DEPOLARIZE2(0.001) 3 10 4 11
        DEPOLARIZE1(0.001) 0 1 2 5 6 7 8 9 12 13 14 15 16
        TICK
        CZ 0 10 1 11
        DEPOLARIZE2(0.001) 0 10 1 11
        DEPOLARIZE1(0.001) 2 3 4 5 6 7 8 9 12 13 14 15 16
        TICK
        H 10 11
        DEPOLARIZE1(0.001) 10 11 0 1 2 3 4 5 6 7 8 9 12 13 14 15 16
        TICK
        M(0.001) 10 12 11
        DETECTOR(0.5, -0.5, 0, 999) rec[-3]
        DETECTOR(0.5, 1.5, 0, 999) rec[-2]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 10 12 11 0 1 2 3 4 5 6 7 8 9 13 14 15 16
        TICK
        R 10 12 11
        X_ERROR(0.001) 10 12 11
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 8 9 13 14 15 16
        TICK
        H 10 11 12
        DEPOLARIZE1(0.001) 10 11 12 0 1 2 3 4 5 6 7 8 9 13 14 15 16
        TICK
        CZ 0 10 1 11
        DEPOLARIZE2(0.001) 0 10 1 11
        DEPOLARIZE1(0.001) 2 3 4 5 6 7 8 9 12 13 14 15 16
        TICK
        H 0 1
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16
        TICK
        CZ 0 11 3 10
        DEPOLARIZE2(0.001) 0 11 3 10
        DEPOLARIZE1(0.001) 1 2 4 5 6 7 8 9 12 13 14 15 16
        TICK
        CZ 1 12 4 11
        DEPOLARIZE2(0.001) 1 12 4 11
        DEPOLARIZE1(0.001) 0 2 3 5 6 7 8 9 10 13 14 15 16
        TICK
        H 1 3 4
        DEPOLARIZE1(0.001) 1 3 4 0 2 5 6 7 8 9 10 11 12 13 14 15 16
        TICK
        CZ 3 11 4 12
        DEPOLARIZE2(0.001) 3 11 4 12
        DEPOLARIZE1(0.001) 0 1 2 5 6 7 8 9 10 13 14 15 16
        TICK
        H 3 10 11 12
        DEPOLARIZE1(0.001) 3 10 11 12 0 1 2 4 5 6 7 8 9 13 14 15 16
        TICK
        M(0.001) 10 12 11
        DETECTOR(0.5, -0.5, 0, 999) rec[-6] rec[-3]
        DETECTOR(0.5, 0.5, 0, 999) rec[-4] rec[-1]
        DETECTOR(0.5, 1.5, 0, 999) rec[-5] rec[-2]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 10 12 11 0 1 2 3 4 5 6 7 8 9 13 14 15 16
        TICK
        R 10 12 13 15 2 5 8 6 7 9 11 14 16
        X_ERROR(0.001) 10 12 13 15 2 5 8 6 7 9 11 14 16
        DEPOLARIZE1(0.001) 0 1 3 4
        TICK
        H 0 5 8 9 10 11 12 13 14 15 16
        DEPOLARIZE1(0.001) 0 5 8 9 10 11 12 13 14 15 16 1 2 3 4 6 7
        TICK
        CZ 0 10 1 11 2 12 4 13 5 14 7 16
        DEPOLARIZE2(0.001) 0 10 1 11 2 12 4 13 5 14 7 16
        DEPOLARIZE1(0.001) 3 6 8 9 15
        TICK
        H 0 1 2 4 5 7
        DEPOLARIZE1(0.001) 0 1 2 4 5 7 3 6 8 9 10 11 12 13 14 15 16
        TICK
        CZ 0 11 3 10 4 14 5 12 6 16 7 13
        DEPOLARIZE2(0.001) 0 11 3 10 4 14 5 12 6 16 7 13
        DEPOLARIZE1(0.001) 1 2 8 9 15
        TICK
        CZ 1 12 2 9 3 13 4 11 5 15 8 14
        DEPOLARIZE2(0.001) 1 12 2 9 3 13 4 11 5 15 8 14
        DEPOLARIZE1(0.001) 0 6 7 10 16
        TICK
        H 1 3 4 5 6 7 8 16
        DEPOLARIZE1(0.001) 1 3 4 5 6 7 8 16 0 2 9 10 11 12 13 14 15
        TICK
        CZ 1 9 3 11 4 12 6 13 7 14 8 15
        DEPOLARIZE2(0.001) 1 9 3 11 4 12 6 13 7 14 8 15
        DEPOLARIZE1(0.001) 0 2 5 10 16
        TICK
        H 4 6 8 9 10 11 12 13 14 15
        DEPOLARIZE1(0.001) 4 6 8 9 10 11 12 13 14 15 0 1 2 3 5 7 16
        TICK
        M(0.001) 10 12 13 15 9 11 14 16
        DETECTOR(0.5, -0.5, 0) rec[-11] rec[-8]
        DETECTOR(0.5, 0.5, 0) rec[-9] rec[-3]
        DETECTOR(0.5, 1.5, 0) rec[-10] rec[-7]
        DETECTOR(1.5, 2.5, 0) rec[-5]
        DETECTOR(2.5, 0.5, 0) rec[-1]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 10 12 13 15 9 11 14 16 0 1 2 3 4 5 6 7 8
        TICK
        REPEAT 4 {
            R 10 12 13 15 9 11 14 16
            X_ERROR(0.001) 10 12 13 15 9 11 14 16
            DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 8
            TICK
            H 0 2 4 9 10 11 12 13 14 15 16
            DEPOLARIZE1(0.001) 0 2 4 9 10 11 12 13 14 15 16 1 3 5 6 7 8
            TICK
            CZ 0 10 1 11 2 12 4 13 5 14 7 16
            DEPOLARIZE2(0.001) 0 10 1 11 2 12 4 13 5 14 7 16
            DEPOLARIZE1(0.001) 3 6 8 9 15
            TICK
            H 0 1 2 3 4 5 7
            DEPOLARIZE1(0.001) 0 1 2 3 4 5 7 6 8 9 10 11 12 13 14 15 16
            TICK
            CZ 0 11 3 10 4 14 5 12 6 16 7 13
            DEPOLARIZE2(0.001) 0 11 3 10 4 14 5 12 6 16 7 13
            DEPOLARIZE1(0.001) 1 2 8 9 15
            TICK
            CZ 1 12 2 9 3 13 4 11 5 15 8 14
            DEPOLARIZE2(0.001) 1 12 2 9 3 13 4 11 5 15 8 14
            DEPOLARIZE1(0.001) 0 6 7 10 16
            TICK
            H 1 3 4 5 6 7 8 16
            DEPOLARIZE1(0.001) 1 3 4 5 6 7 8 16 0 2 9 10 11 12 13 14 15
            TICK
            CZ 1 9 3 11 4 12 6 13 7 14 8 15
            DEPOLARIZE2(0.001) 1 9 3 11 4 12 6 13 7 14 8 15
            DEPOLARIZE1(0.001) 0 2 5 10 16
            TICK
            H 4 6 8 9 10 11 12 13 14 15
            DEPOLARIZE1(0.001) 4 6 8 9 10 11 12 13 14 15 0 1 2 3 5 7 16
            TICK
            M(0.001) 10 12 13 15 9 11 14 16
            DETECTOR(-0.5, 1.5, 0) rec[-12] rec[-4]
            DETECTOR(0.5, -0.5, 0) rec[-16] rec[-8]
            DETECTOR(0.5, 0.5, 0) rec[-11] rec[-3]
            DETECTOR(0.5, 1.5, 0) rec[-15] rec[-7]
            DETECTOR(1.5, 0.5, 0) rec[-14] rec[-6]
            DETECTOR(1.5, 1.5, 0) rec[-10] rec[-2]
            DETECTOR(1.5, 2.5, 0) rec[-13] rec[-5]
            DETECTOR(2.5, 0.5, 0) rec[-9] rec[-1]
            SHIFT_COORDS(0, 0, 1)
            DEPOLARIZE1(0.001) 10 12 13 15 9 11 14 16 0 1 2 3 4 5 6 7 8
            TICK
        }
        R 10 12 13 15 9 11 14 16
        X_ERROR(0.001) 10 12 13 15 9 11 14 16
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 8
        TICK
        H 0 2 4 9 10 11 12 13 14 15 16
        DEPOLARIZE1(0.001) 0 2 4 9 10 11 12 13 14 15 16 1 3 5 6 7 8
        TICK
        CZ 0 10 1 11 2 12 4 13 5 14 7 16
        DEPOLARIZE2(0.001) 0 10 1 11 2 12 4 13 5 14 7 16
        DEPOLARIZE1(0.001) 3 6 8 9 15
        TICK
        H 0 1 2 3 4 5 7
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 7 6 8 9 10 11 12 13 14 15 16
        TICK
        CZ 0 11 3 10 4 14 5 12 6 16 7 13
        DEPOLARIZE2(0.001) 0 11 3 10 4 14 5 12 6 16 7 13
        DEPOLARIZE1(0.001) 1 2 8 9 15
        TICK
        CZ 1 12 2 9 3 13 4 11 5 15 8 14
        DEPOLARIZE2(0.001) 1 12 2 9 3 13 4 11 5 15 8 14
        DEPOLARIZE1(0.001) 0 6 7 10 16
        TICK
        H 1 2 3 4 6 7 8 16
        DEPOLARIZE1(0.001) 1 2 3 4 6 7 8 16 0 5 9 10 11 12 13 14 15
        TICK
        CZ 1 9 3 11 4 12 6 13 7 14 8 15
        DEPOLARIZE2(0.001) 1 9 3 11 4 12 6 13 7 14 8 15
        DEPOLARIZE1(0.001) 0 2 5 10 16
        TICK
        H 0 1 3 7 9 10 11 12 13 14 15
        DEPOLARIZE1(0.001) 0 1 3 7 9 10 11 12 13 14 15 2 4 5 6 8 16
        TICK
        M(0.001) 10 12 13 15 0 1 2 3 4 5 6 7 8 9 11 14 16
        DETECTOR(-0.5, 1.5, 0) rec[-21] rec[-4]
        DETECTOR(0.5, -0.5, 0) rec[-25] rec[-17]
        DETECTOR(0.5, 0.5, 0) rec[-20] rec[-3]
        DETECTOR(0.5, 1.5, 0) rec[-24] rec[-16]
        DETECTOR(1.5, 0.5, 0) rec[-23] rec[-15]
        DETECTOR(1.5, 1.5, 0) rec[-19] rec[-2]
        DETECTOR(1.5, 2.5, 0) rec[-22] rec[-14]
        DETECTOR(2.5, 0.5, 0) rec[-18] rec[-1]
        DETECTOR(0.5, -0.5, 0) rec[-17] rec[-13] rec[-10]
        DETECTOR(0.5, 1.5, 0) rec[-16] rec[-12] rec[-11] rec[-9] rec[-8]
        DETECTOR(1.5, 0.5, 0) rec[-15] rec[-10] rec[-9] rec[-7] rec[-6]
        DETECTOR(1.5, 2.5, 0) rec[-14] rec[-8] rec[-5]
        OBSERVABLE_INCLUDE(0) rec[-13] rec[-12] rec[-11]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 10 12 13 15 0 1 2 3 4 5 6 7 8 9 11 14 16
    """)