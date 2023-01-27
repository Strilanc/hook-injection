import stim

from hookinj.gen._noise import _measure_basis, _iter_split_op_moments, occurs_in_classical_control_system, NoiseModel
from hookinj.gen._util import estimate_qubit_count_during_postselection


def test_estimate_qubit_count_during_postselection():
    assert estimate_qubit_count_during_postselection(stim.Circuit("""
        QUBIT_COORDS(0, 0) 100
        H 55
        M 55
    """)) == 0

    assert estimate_qubit_count_during_postselection(stim.Circuit("""
        QUBIT_COORDS(0, 0) 100
        H 55
        M 55
        DETECTOR(0, 0, 0, 999) rec[-1]
    """)) == 1

    assert estimate_qubit_count_during_postselection(stim.Circuit("""
        QUBIT_COORDS(0, 0) 100
        H 55 56
        M 55
        DETECTOR(0, 0, 0, 999) rec[-1]
    """)) == 2

    assert estimate_qubit_count_during_postselection(stim.Circuit("""
        QUBIT_COORDS(0, 0) 100
        H 55 56
        M 55
        DETECTOR(0, 0, 0, 999) rec[-1]
        H 57
    """)) == 2

    assert estimate_qubit_count_during_postselection(stim.Circuit("""
        QUBIT_COORDS(0, 0) 100
        H 55 56
        M 55
        REPEAT 10 {
            H 58
        }
        DETECTOR(0, 0, 0, 999) rec[-1]
        H 57
    """)) == 3
