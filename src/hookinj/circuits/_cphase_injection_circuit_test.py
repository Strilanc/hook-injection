import itertools

import pytest
import stim

from hookinj import gen
from hookinj._make_circuit import make_circuit
from hookinj.circuits._cphase_injection_circuit import zz_inject_xzzx_round, \
    make_zz_injection
from hookinj.circuits._hook_injection_circuit_test import count_d1_and_d2_errors


@pytest.mark.parametrize('prev_d,next_d,basis,tweaked', itertools.product(
    [0, 2, 3, 4, 5],
    [0, 2, 3, 4, 5],
    'XY',
    [False, True],
))
def test_zz_inject_xzzx_round(prev_d: int, next_d: int, basis: str, tweaked: bool):
    if next_d == 0 == prev_d:
        return
    if next_d == 0 and basis == 'Y':
        return
    chunk = zz_inject_xzzx_round(
        next_d=next_d,
        prev_d=prev_d,
        basis=basis,
        tweaked=tweaked,
    )
    chunk.verify()


@pytest.mark.parametrize('injection_basis,distance,memory_rounds,postselected_rounds,postselected_diameter,magic_measurement', itertools.product(
    'XY',
    [3, 4, 5],
    [3, 4],
    [2, 3],
    [2, 3],
    [False, True],
))
def test_make_zz_injection(
    injection_basis: str,
    distance: int,
    memory_rounds: int,
    postselected_rounds: int,
    postselected_diameter: int,
    magic_measurement: bool,
):
    if not magic_measurement and injection_basis == 'Y':
        return

    circuit = gen.compile_chunks_into_circuit(make_zz_injection(
        injection_basis=injection_basis,
        distance=distance,
        memory_rounds=memory_rounds,
        postselected_rounds=postselected_rounds,
        postselected_diameter=postselected_diameter,
        magic_measurement=magic_measurement,
    ))
    circuit.detector_error_model(decompose_errors=True)


def test_make_zz_circuit():
    make_circuit(
        basis='zz_inject_X',
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        memory_rounds=3,
        distance=5,
        postselected_diameter=3,
        postselected_rounds=2,
        convert_to_cz=False,
    ).detector_error_model(decompose_errors=True)

    c = make_circuit(
        basis='zz_inject_Y_magic_verify',
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        memory_rounds=3,
        distance=7,
        postselected_diameter=5,
        postselected_rounds=2,
        convert_to_cz=True,
    )
    assert c.detector_error_model(decompose_errors=True) is not None
    num_d1, num_d2 = count_d1_and_d2_errors(c)
    assert num_d1 == 21
    assert num_d2 == 487

    # tweaked
    c = make_circuit(
        basis='zz_tweaked_inject_Y_magic_verify',
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        memory_rounds=3,
        distance=7,
        postselected_diameter=5,
        postselected_rounds=2,
        convert_to_cz=True,
    )
    assert c.detector_error_model(decompose_errors=True) is not None
    num_d1, num_d2 = count_d1_and_d2_errors(c)
    assert num_d1 == 8
    assert num_d2 == 235


def test_exact_circuit():
    assert make_circuit(
        basis='zz_inject_Y_magic_verify',
        noise=gen.NoiseModel.uniform_depolarizing(1e-3),
        memory_rounds=2,
        distance=3,
        postselected_diameter=2,
        postselected_rounds=2,
        convert_to_cz=True,
    ) == stim.Circuit("""
        QUBIT_COORDS(0, 0) 0
        QUBIT_COORDS(0, 1) 1
        QUBIT_COORDS(0, 2) 2
        QUBIT_COORDS(0, 3) 3
        QUBIT_COORDS(0, 4) 4
        QUBIT_COORDS(1, 0) 5
        QUBIT_COORDS(1, 1) 6
        QUBIT_COORDS(1, 2) 7
        QUBIT_COORDS(1, 3) 8
        QUBIT_COORDS(1, 4) 9
        QUBIT_COORDS(2, 0) 10
        QUBIT_COORDS(2, 1) 11
        QUBIT_COORDS(2, 2) 12
        QUBIT_COORDS(2, 3) 13
        QUBIT_COORDS(2, 4) 14
        QUBIT_COORDS(3, 0) 15
        QUBIT_COORDS(3, 1) 16
        QUBIT_COORDS(3, 2) 17
        QUBIT_COORDS(3, 3) 18
        QUBIT_COORDS(3, 4) 19
        QUBIT_COORDS(4, 0) 20
        QUBIT_COORDS(4, 1) 21
        QUBIT_COORDS(4, 2) 22
        QUBIT_COORDS(4, 3) 23
        QUBIT_COORDS(4, 4) 24
        R 0 1 2 5 7 10 11 12 6
        X_ERROR(0.001) 0 1 2 5 7 10 11 12 6
        DEPOLARIZE1(0.001) 3 4 8 9 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        C_ZYX 0 10
        H 1 5 6 7 11 12
        DEPOLARIZE1(0.001) 0 10 1 5 6 7 11 12 2 3 4 8 9 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 0 10
        DEPOLARIZE2(0.001) 0 10
        DEPOLARIZE1(0.001) 1 2 3 4 5 6 7 8 9 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 0
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 0 5 2 7 6 11
        DEPOLARIZE2(0.001) 0 5 2 7 6 11
        DEPOLARIZE1(0.001) 1 3 4 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 0 2 6
        DEPOLARIZE1(0.001) 0 2 6 1 3 4 5 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 0 1 6 7 10 11
        DEPOLARIZE2(0.001) 0 1 6 7 10 11
        DEPOLARIZE1(0.001) 2 3 4 5 8 9 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 1 2 5 6 11 12
        DEPOLARIZE2(0.001) 1 2 5 6 11 12
        DEPOLARIZE1(0.001) 0 3 4 7 8 9 10 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 6 10 12
        DEPOLARIZE1(0.001) 6 10 12 0 1 2 3 4 5 7 8 9 11 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 1 6 5 10 7 12
        DEPOLARIZE2(0.001) 1 6 5 10 7 12
        DEPOLARIZE1(0.001) 0 2 3 4 8 9 11 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 1 5 7 10 11 12
        DEPOLARIZE1(0.001) 1 5 7 10 11 12 0 2 3 4 6 8 9 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        M(0.001) 1 5 7 11
        DETECTOR(1, 0, 0, 999) rec[-3]
        DETECTOR(1, 2, 0, 999) rec[-2]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 1 5 7 11 0 2 3 4 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        R 1 5 7 11
        X_ERROR(0.001) 1 5 7 11
        DEPOLARIZE1(0.001) 0 2 3 4 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 0 1 2 5 7 11
        DEPOLARIZE1(0.001) 0 1 2 5 7 11 3 4 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 0 5 2 7 6 11
        DEPOLARIZE2(0.001) 0 5 2 7 6 11
        DEPOLARIZE1(0.001) 1 3 4 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 0 2 6
        DEPOLARIZE1(0.001) 0 2 6 1 3 4 5 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 0 1 6 7 10 11
        DEPOLARIZE2(0.001) 0 1 6 7 10 11
        DEPOLARIZE1(0.001) 2 3 4 5 8 9 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 1 2 5 6 11 12
        DEPOLARIZE2(0.001) 1 2 5 6 11 12
        DEPOLARIZE1(0.001) 0 3 4 7 8 9 10 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 6 10 12
        DEPOLARIZE1(0.001) 6 10 12 0 1 2 3 4 5 7 8 9 11 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        CZ 1 6 5 10 7 12
        DEPOLARIZE2(0.001) 1 6 5 10 7 12
        DEPOLARIZE1(0.001) 0 2 3 4 8 9 11 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        H 1 5 7 11
        DEPOLARIZE1(0.001) 1 5 7 11 0 2 3 4 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        M(0.001) 1 5 7 11
        DETECTOR(1, 0, 0, 999) rec[-7] rec[-3]
        DETECTOR(0, 1, 0, 999) rec[-8] rec[-4]
        DETECTOR(2, 1, 0, 999) rec[-5] rec[-1]
        DETECTOR(1, 2, 0, 999) rec[-6] rec[-2]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 1 5 7 11 0 2 3 4 6 8 9 10 12 13 14 15 16 17 18 19 20 21 22 23 24
        TICK
        R 1 3 4 5 7 9 11 13 14 15 16 17 19 21 23 24 8 18 20 22
        X_ERROR(0.001) 1 3 4 5 7 9 11 13 14 15 16 17 19 21 23 24 8 18 20 22
        DEPOLARIZE1(0.001) 0 2 6 10 12
        TICK
        H 0 1 2 3 5 7 8 9 11 13 15 17 18 19 21 23 24
        DEPOLARIZE1(0.001) 0 1 2 3 5 7 8 9 11 13 15 17 18 19 21 23 24 4 6 10 12 14 16 20 22
        TICK
        CZ 0 5 2 7 4 9 6 11 8 13 10 15 12 17 14 19 16 21 18 23
        DEPOLARIZE2(0.001) 0 5 2 7 4 9 6 11 8 13 10 15 12 17 14 19 16 21 18 23
        DEPOLARIZE1(0.001) 1 3 20 22 24
        TICK
        H 0 2 4 6 8 10 12 14 16 18
        DEPOLARIZE1(0.001) 0 2 4 6 8 10 12 14 16 18 1 3 5 7 9 11 13 15 17 19 20 21 22 23 24
        TICK
        CZ 0 1 2 3 6 7 8 9 10 11 12 13 16 17 18 19 20 21 22 23
        DEPOLARIZE2(0.001) 0 1 2 3 6 7 8 9 10 11 12 13 16 17 18 19 20 21 22 23
        DEPOLARIZE1(0.001) 4 5 14 15 24
        TICK
        CZ 1 2 3 4 5 6 7 8 11 12 13 14 15 16 17 18 21 22 23 24
        DEPOLARIZE2(0.001) 1 2 3 4 5 6 7 8 11 12 13 14 15 16 17 18 21 22 23 24
        DEPOLARIZE1(0.001) 0 9 10 19 20
        TICK
        H 6 8 10 12 14 16 18 20 22 24
        DEPOLARIZE1(0.001) 6 8 10 12 14 16 18 20 22 24 0 1 2 3 4 5 7 9 11 13 15 17 19 21 23
        TICK
        CZ 1 6 3 8 5 10 7 12 9 14 11 16 13 18 15 20 17 22 19 24
        DEPOLARIZE2(0.001) 1 6 3 8 5 10 7 12 9 14 11 16 13 18 15 20 17 22 19 24
        DEPOLARIZE1(0.001) 0 2 4 21 23
        TICK
        H 1 3 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24
        DEPOLARIZE1(0.001) 1 3 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 0 2 4
        TICK
        M(0.001) 1 3 5 7 9 11 13 15 17 19 21 23
        DETECTOR(1, 0, 0) rec[-15] rec[-10]
        DETECTOR(0, 1, 0) rec[-16] rec[-12]
        DETECTOR(2, 1, 0) rec[-13] rec[-7]
        DETECTOR(1, 2, 0) rec[-14] rec[-9]
        DETECTOR(4, 1, 0) rec[-2]
        DETECTOR(1, 4, 0) rec[-8]
        DETECTOR(3, 4, 0) rec[-3]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 1 3 5 7 9 11 13 15 17 19 21 23 0 2 4 6 8 10 12 14 16 18 20 22 24
        MPP X0*Z6*X10 X10*Z16*X20 Z0*Z2*X6 X6*Z10*Z12*X16 X2*Z6*Z8*X12 X16*Z20*Z22 X12*Z16*Z18*X22 Z2*Z4*X8 X8*Z12*Z14*X18 X4*Z8*X14 X18*Z22*Z24 X14*Z18*X24 Y0*X2*X4*Z10*Z20
        DETECTOR(1, 0, 0) rec[-23] rec[-13]
        DETECTOR(3, 0, 0) rec[-18] rec[-12]
        DETECTOR(0, 1, 0) rec[-25] rec[-11]
        DETECTOR(2, 1, 0) rec[-20] rec[-10]
        DETECTOR(1, 2, 0) rec[-22] rec[-9]
        DETECTOR(4, 1, 0) rec[-15] rec[-8]
        DETECTOR(3, 2, 0) rec[-17] rec[-7]
        DETECTOR(0, 3, 0) rec[-24] rec[-6]
        DETECTOR(2, 3, 0) rec[-19] rec[-5]
        DETECTOR(1, 4, 0) rec[-21] rec[-4]
        DETECTOR(4, 3, 0) rec[-14] rec[-3]
        DETECTOR(3, 4, 0) rec[-16] rec[-2]
        OBSERVABLE_INCLUDE(0) rec[-1]
        SHIFT_COORDS(0, 0, 1)
        TICK
    """)
