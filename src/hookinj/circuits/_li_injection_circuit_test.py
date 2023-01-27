import itertools

import pytest
import stim

from hookinj import gen
from hookinj.circuits._li_injection_circuit import make_li_injection_rounds


@pytest.mark.parametrize("b,d,m", itertools.product('XYZ', [5, 7, 9], [False, True]))
def test_make_li_injection_rounds(b: str, d: int, m: bool):
    if b == 'Y' and not m:
        return

    chunks = make_li_injection_rounds(injection_basis=b, distance=d, memory_rounds=5, postselected_rounds=3, postselected_diameter=2, magic_measurement=True)
    for c in chunks:
        c.verify()

    circuit = gen.compile_chunks_into_circuit(chunks)
    circuit.detector_error_model(decompose_errors=True)


def test_make_li_injection_exact_circuit():
    chunks = make_li_injection_rounds(injection_basis='Y', distance=5, memory_rounds=3, postselected_rounds=2, postselected_diameter=3, magic_measurement=True)
    circuit = gen.compile_chunks_into_circuit(chunks)
    assert circuit == stim.Circuit("""
        QUBIT_COORDS(0, 0) 0
        QUBIT_COORDS(0, 1) 1
        QUBIT_COORDS(0, 2) 2
        QUBIT_COORDS(0, 3) 3
        QUBIT_COORDS(0, 4) 4
        QUBIT_COORDS(0, 5) 5
        QUBIT_COORDS(0, 6) 6
        QUBIT_COORDS(0, 7) 7
        QUBIT_COORDS(0, 8) 8
        QUBIT_COORDS(1, 0) 9
        QUBIT_COORDS(1, 1) 10
        QUBIT_COORDS(1, 2) 11
        QUBIT_COORDS(1, 3) 12
        QUBIT_COORDS(1, 4) 13
        QUBIT_COORDS(1, 5) 14
        QUBIT_COORDS(1, 6) 15
        QUBIT_COORDS(1, 7) 16
        QUBIT_COORDS(1, 8) 17
        QUBIT_COORDS(2, 0) 18
        QUBIT_COORDS(2, 1) 19
        QUBIT_COORDS(2, 2) 20
        QUBIT_COORDS(2, 3) 21
        QUBIT_COORDS(2, 4) 22
        QUBIT_COORDS(2, 5) 23
        QUBIT_COORDS(2, 6) 24
        QUBIT_COORDS(2, 7) 25
        QUBIT_COORDS(2, 8) 26
        QUBIT_COORDS(3, 0) 27
        QUBIT_COORDS(3, 1) 28
        QUBIT_COORDS(3, 2) 29
        QUBIT_COORDS(3, 3) 30
        QUBIT_COORDS(3, 4) 31
        QUBIT_COORDS(3, 5) 32
        QUBIT_COORDS(3, 6) 33
        QUBIT_COORDS(3, 7) 34
        QUBIT_COORDS(3, 8) 35
        QUBIT_COORDS(4, 0) 36
        QUBIT_COORDS(4, 1) 37
        QUBIT_COORDS(4, 2) 38
        QUBIT_COORDS(4, 3) 39
        QUBIT_COORDS(4, 4) 40
        QUBIT_COORDS(4, 5) 41
        QUBIT_COORDS(4, 6) 42
        QUBIT_COORDS(4, 7) 43
        QUBIT_COORDS(4, 8) 44
        QUBIT_COORDS(5, 0) 45
        QUBIT_COORDS(5, 1) 46
        QUBIT_COORDS(5, 2) 47
        QUBIT_COORDS(5, 3) 48
        QUBIT_COORDS(5, 4) 49
        QUBIT_COORDS(5, 5) 50
        QUBIT_COORDS(5, 6) 51
        QUBIT_COORDS(5, 7) 52
        QUBIT_COORDS(5, 8) 53
        QUBIT_COORDS(6, 0) 54
        QUBIT_COORDS(6, 1) 55
        QUBIT_COORDS(6, 2) 56
        QUBIT_COORDS(6, 3) 57
        QUBIT_COORDS(6, 4) 58
        QUBIT_COORDS(6, 5) 59
        QUBIT_COORDS(6, 6) 60
        QUBIT_COORDS(6, 7) 61
        QUBIT_COORDS(6, 8) 62
        QUBIT_COORDS(7, 0) 63
        QUBIT_COORDS(7, 1) 64
        QUBIT_COORDS(7, 2) 65
        QUBIT_COORDS(7, 3) 66
        QUBIT_COORDS(7, 4) 67
        QUBIT_COORDS(7, 5) 68
        QUBIT_COORDS(7, 6) 69
        QUBIT_COORDS(7, 7) 70
        QUBIT_COORDS(7, 8) 71
        QUBIT_COORDS(8, 0) 72
        QUBIT_COORDS(8, 1) 73
        QUBIT_COORDS(8, 2) 74
        QUBIT_COORDS(8, 3) 75
        QUBIT_COORDS(8, 4) 76
        QUBIT_COORDS(8, 5) 77
        QUBIT_COORDS(8, 6) 78
        QUBIT_COORDS(8, 7) 79
        QUBIT_COORDS(8, 8) 80
        RX 9 11 13 27 29 31 2 4 10 12 20 22 30 40
        RY 0
        R 18 28 36 38 1 3 19 21 37 39
        TICK
        CX 2 1 4 3 20 19 22 21 38 37 40 39
        TICK
        CX 0 1 2 3 18 19 20 21 36 37 38 39
        TICK
        CX 9 18 10 1 11 20 12 3 13 22 27 36 28 19 29 38 30 21 31 40
        TICK
        CX 9 0 10 19 11 2 12 21 13 4 27 18 28 37 29 20 30 39 31 22
        TICK
        CX 9 10 11 12 27 28 29 30
        TICK
        CX 11 10 13 12 29 28 31 30
        TICK
        MX 9 11 13 27 29 31
        M 1 3 19 21 37 39
        DETECTOR(1, 2, 0, 999) rec[-11]
        DETECTOR(1, 4, 0, 999) rec[-10]
        DETECTOR(3, 4, 0, 999) rec[-7]
        DETECTOR(4, 1, 0, 999) rec[-2]
        SHIFT_COORDS(0, 0, 1)
        TICK
        RX 9 11 13 27 29 31
        R 1 3 19 21 37 39
        TICK
        CX 2 1 4 3 20 19 22 21 38 37 40 39
        TICK
        CX 0 1 2 3 18 19 20 21 36 37 38 39
        TICK
        CX 9 18 10 1 11 20 12 3 13 22 27 36 28 19 29 38 30 21 31 40
        TICK
        CX 9 0 10 19 11 2 12 21 13 4 27 18 28 37 29 20 30 39 31 22
        TICK
        CX 9 10 11 12 27 28 29 30
        TICK
        CX 11 10 13 12 29 28 31 30
        TICK
        MX 9 11 13 27 29 31
        M 1 3 19 21 37 39
        DETECTOR(0, 1, 0, 999) rec[-18] rec[-6]
        DETECTOR(0, 3, 0, 999) rec[-17] rec[-5]
        DETECTOR(1, 0, 0, 999) rec[-24] rec[-12]
        DETECTOR(1, 2, 0, 999) rec[-23] rec[-11]
        DETECTOR(1, 4, 0, 999) rec[-22] rec[-10]
        DETECTOR(2, 1, 0, 999) rec[-16] rec[-4]
        DETECTOR(2, 3, 0, 999) rec[-15] rec[-3]
        DETECTOR(3, 0, 0, 999) rec[-21] rec[-9]
        DETECTOR(3, 2, 0, 999) rec[-20] rec[-8]
        DETECTOR(3, 4, 0, 999) rec[-19] rec[-7]
        DETECTOR(4, 1, 0, 999) rec[-14] rec[-2]
        DETECTOR(4, 3, 0, 999) rec[-13] rec[-1]
        SHIFT_COORDS(0, 0, 1)
        TICK
        RX 9 11 13 15 17 27 29 31 33 35 45 47 49 51 53 63 65 67 69 71 6 8 14 16 24 26 32 34 42 44 50 52 60 62 70 80
        R 46 48 54 56 58 64 66 68 72 74 76 78 1 3 5 7 19 21 23 25 37 39 41 43 55 57 59 61 73 75 77 79
        TICK
        CX 9 18 10 1 11 20 12 3 13 22 14 5 15 24 16 7 17 26 27 36 28 19 29 38 30 21 31 40 32 23 33 42 34 25 35 44 45 54 46 37 47 56 48 39 49 58 50 41 51 60 52 43 53 62 63 72 64 55 65 74 66 57 67 76 68 59 69 78 70 61 71 80
        TICK
        CX 0 1 2 3 4 5 6 7 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 27 28 29 30 31 32 33 34 36 37 38 39 40 41 42 43 45 46 47 48 49 50 51 52 54 55 56 57 58 59 60 61 63 64 65 66 67 68 69 70 72 73 74 75 76 77 78 79
        TICK
        CX 2 1 4 3 6 5 8 7 11 10 13 12 15 14 17 16 20 19 22 21 24 23 26 25 29 28 31 30 33 32 35 34 38 37 40 39 42 41 44 43 47 46 49 48 51 50 53 52 56 55 58 57 60 59 62 61 65 64 67 66 69 68 71 70 74 73 76 75 78 77 80 79
        TICK
        CX 9 0 10 19 11 2 12 21 13 4 14 23 15 6 16 25 17 8 27 18 28 37 29 20 30 39 31 22 32 41 33 24 34 43 35 26 45 36 46 55 47 38 48 57 49 40 50 59 51 42 52 61 53 44 63 54 64 73 65 56 66 75 67 58 68 77 69 60 70 79 71 62
        TICK
        MX 9 11 13 15 17 27 29 31 33 35 45 47 49 51 53 63 65 67 69 71
        M 1 3 5 7 19 21 23 25 37 39 41 43 55 57 59 61 73 75 77 79
        DETECTOR(0, 1, 0) rec[-46] rec[-20]
        DETECTOR(0, 3, 0) rec[-45] rec[-19]
        DETECTOR(1, 0, 0) rec[-52] rec[-40]
        DETECTOR(1, 2, 0) rec[-51] rec[-39]
        DETECTOR(1, 4, 0) rec[-50] rec[-38]
        DETECTOR(1, 6, 0) rec[-37]
        DETECTOR(1, 8, 0) rec[-36]
        DETECTOR(2, 1, 0) rec[-44] rec[-16]
        DETECTOR(2, 3, 0) rec[-43] rec[-15]
        DETECTOR(3, 0, 0) rec[-49] rec[-35]
        DETECTOR(3, 2, 0) rec[-48] rec[-34]
        DETECTOR(3, 4, 0) rec[-47] rec[-33]
        DETECTOR(3, 6, 0) rec[-32]
        DETECTOR(3, 8, 0) rec[-31]
        DETECTOR(4, 1, 0) rec[-42] rec[-12]
        DETECTOR(4, 3, 0) rec[-41] rec[-11]
        DETECTOR(5, 6, 0) rec[-27]
        DETECTOR(5, 8, 0) rec[-26]
        DETECTOR(6, 1, 0) rec[-8]
        DETECTOR(6, 3, 0) rec[-7]
        DETECTOR(7, 8, 0) rec[-21]
        DETECTOR(8, 1, 0) rec[-4]
        DETECTOR(8, 3, 0) rec[-3]
        DETECTOR(8, 5, 0) rec[-2]
        SHIFT_COORDS(0, 0, 1)
        TICK
        REPEAT 2 {
            RX 9 11 13 15 17 27 29 31 33 35 45 47 49 51 53 63 65 67 69 71
            R 1 3 5 7 19 21 23 25 37 39 41 43 55 57 59 61 73 75 77 79
            TICK
            CX 9 18 10 1 11 20 12 3 13 22 14 5 15 24 16 7 17 26 27 36 28 19 29 38 30 21 31 40 32 23 33 42 34 25 35 44 45 54 46 37 47 56 48 39 49 58 50 41 51 60 52 43 53 62 63 72 64 55 65 74 66 57 67 76 68 59 69 78 70 61 71 80
            TICK
            CX 0 1 2 3 4 5 6 7 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 27 28 29 30 31 32 33 34 36 37 38 39 40 41 42 43 45 46 47 48 49 50 51 52 54 55 56 57 58 59 60 61 63 64 65 66 67 68 69 70 72 73 74 75 76 77 78 79
            TICK
            CX 2 1 4 3 6 5 8 7 11 10 13 12 15 14 17 16 20 19 22 21 24 23 26 25 29 28 31 30 33 32 35 34 38 37 40 39 42 41 44 43 47 46 49 48 51 50 53 52 56 55 58 57 60 59 62 61 65 64 67 66 69 68 71 70 74 73 76 75 78 77 80 79
            TICK
            CX 9 0 10 19 11 2 12 21 13 4 14 23 15 6 16 25 17 8 27 18 28 37 29 20 30 39 31 22 32 41 33 24 34 43 35 26 45 36 46 55 47 38 48 57 49 40 50 59 51 42 52 61 53 44 63 54 64 73 65 56 66 75 67 58 68 77 69 60 70 79 71 62
            TICK
            MX 9 11 13 15 17 27 29 31 33 35 45 47 49 51 53 63 65 67 69 71
            M 1 3 5 7 19 21 23 25 37 39 41 43 55 57 59 61 73 75 77 79
            DETECTOR(0, 1, 0) rec[-60] rec[-20]
            DETECTOR(0, 3, 0) rec[-59] rec[-19]
            DETECTOR(0, 5, 0) rec[-58] rec[-18]
            DETECTOR(0, 7, 0) rec[-57] rec[-17]
            DETECTOR(1, 0, 0) rec[-80] rec[-40]
            DETECTOR(1, 2, 0) rec[-79] rec[-39]
            DETECTOR(1, 4, 0) rec[-78] rec[-38]
            DETECTOR(1, 6, 0) rec[-77] rec[-37]
            DETECTOR(1, 8, 0) rec[-76] rec[-36]
            DETECTOR(2, 1, 0) rec[-56] rec[-16]
            DETECTOR(2, 3, 0) rec[-55] rec[-15]
            DETECTOR(2, 5, 0) rec[-54] rec[-14]
            DETECTOR(2, 7, 0) rec[-53] rec[-13]
            DETECTOR(3, 0, 0) rec[-75] rec[-35]
            DETECTOR(3, 2, 0) rec[-74] rec[-34]
            DETECTOR(3, 4, 0) rec[-73] rec[-33]
            DETECTOR(3, 6, 0) rec[-72] rec[-32]
            DETECTOR(3, 8, 0) rec[-71] rec[-31]
            DETECTOR(4, 1, 0) rec[-52] rec[-12]
            DETECTOR(4, 3, 0) rec[-51] rec[-11]
            DETECTOR(4, 5, 0) rec[-50] rec[-10]
            DETECTOR(4, 7, 0) rec[-49] rec[-9]
            DETECTOR(5, 0, 0) rec[-70] rec[-30]
            DETECTOR(5, 2, 0) rec[-69] rec[-29]
            DETECTOR(5, 4, 0) rec[-68] rec[-28]
            DETECTOR(5, 6, 0) rec[-67] rec[-27]
            DETECTOR(5, 8, 0) rec[-66] rec[-26]
            DETECTOR(6, 1, 0) rec[-48] rec[-8]
            DETECTOR(6, 3, 0) rec[-47] rec[-7]
            DETECTOR(6, 5, 0) rec[-46] rec[-6]
            DETECTOR(6, 7, 0) rec[-45] rec[-5]
            DETECTOR(7, 0, 0) rec[-65] rec[-25]
            DETECTOR(7, 2, 0) rec[-64] rec[-24]
            DETECTOR(7, 4, 0) rec[-63] rec[-23]
            DETECTOR(7, 6, 0) rec[-62] rec[-22]
            DETECTOR(7, 8, 0) rec[-61] rec[-21]
            DETECTOR(8, 1, 0) rec[-44] rec[-4]
            DETECTOR(8, 3, 0) rec[-43] rec[-3]
            DETECTOR(8, 5, 0) rec[-42] rec[-2]
            DETECTOR(8, 7, 0) rec[-41] rec[-1]
            SHIFT_COORDS(0, 0, 1)
            TICK
        }
        MPP Z0*Z2*Z10 Z2*Z4*Z12 Z4*Z6*Z14 Z6*Z8*Z16 X0*X10*X18 X2*X10*X12*X20 X4*X12*X14*X22 X6*X14*X16*X24 X8*X16*X26 Z10*Z18*Z20*Z28 Z12*Z20*Z22*Z30 Z14*Z22*Z24*Z32 Z16*Z24*Z26*Z34 X18*X28*X36 X20*X28*X30*X38 X22*X30*X32*X40 X24*X32*X34*X42 X26*X34*X44 Z28*Z36*Z38*Z46 Z30*Z38*Z40*Z48 Z32*Z40*Z42*Z50 Z34*Z42*Z44*Z52 X36*X46*X54 X38*X46*X48*X56 X40*X48*X50*X58 X42*X50*X52*X60 X44*X52*X62 Z46*Z54*Z56*Z64 Z48*Z56*Z58*Z66 Z50*Z58*Z60*Z68 Z52*Z60*Z62*Z70 X54*X64*X72 X56*X64*X66*X74 X58*X66*X68*X76 X60*X68*X70*X78 X62*X70*X80 Z64*Z72*Z74 Z66*Z74*Z76 Z68*Z76*Z78 Z70*Z78*Z80 Y0*X2*X4*X6*X8*Z18*Z36*Z54*Z72
        DETECTOR(0, 1, 0) rec[-61] rec[-41]
        DETECTOR(0, 3, 0) rec[-60] rec[-40]
        DETECTOR(0, 5, 0) rec[-59] rec[-39]
        DETECTOR(0, 7, 0) rec[-58] rec[-38]
        DETECTOR(1, 0, 0) rec[-81] rec[-37]
        DETECTOR(1, 2, 0) rec[-80] rec[-36]
        DETECTOR(1, 4, 0) rec[-79] rec[-35]
        DETECTOR(1, 6, 0) rec[-78] rec[-34]
        DETECTOR(1, 8, 0) rec[-77] rec[-33]
        DETECTOR(2, 1, 0) rec[-57] rec[-32]
        DETECTOR(2, 3, 0) rec[-56] rec[-31]
        DETECTOR(2, 5, 0) rec[-55] rec[-30]
        DETECTOR(2, 7, 0) rec[-54] rec[-29]
        DETECTOR(3, 0, 0) rec[-76] rec[-28]
        DETECTOR(3, 2, 0) rec[-75] rec[-27]
        DETECTOR(3, 4, 0) rec[-74] rec[-26]
        DETECTOR(3, 6, 0) rec[-73] rec[-25]
        DETECTOR(3, 8, 0) rec[-72] rec[-24]
        DETECTOR(4, 1, 0) rec[-53] rec[-23]
        DETECTOR(4, 3, 0) rec[-52] rec[-22]
        DETECTOR(4, 5, 0) rec[-51] rec[-21]
        DETECTOR(4, 7, 0) rec[-50] rec[-20]
        DETECTOR(5, 0, 0) rec[-71] rec[-19]
        DETECTOR(5, 2, 0) rec[-70] rec[-18]
        DETECTOR(5, 4, 0) rec[-69] rec[-17]
        DETECTOR(5, 6, 0) rec[-68] rec[-16]
        DETECTOR(5, 8, 0) rec[-67] rec[-15]
        DETECTOR(6, 1, 0) rec[-49] rec[-14]
        DETECTOR(6, 3, 0) rec[-48] rec[-13]
        DETECTOR(6, 5, 0) rec[-47] rec[-12]
        DETECTOR(6, 7, 0) rec[-46] rec[-11]
        DETECTOR(7, 0, 0) rec[-66] rec[-10]
        DETECTOR(7, 2, 0) rec[-65] rec[-9]
        DETECTOR(7, 4, 0) rec[-64] rec[-8]
        DETECTOR(7, 6, 0) rec[-63] rec[-7]
        DETECTOR(7, 8, 0) rec[-62] rec[-6]
        DETECTOR(8, 1, 0) rec[-45] rec[-5]
        DETECTOR(8, 3, 0) rec[-44] rec[-4]
        DETECTOR(8, 5, 0) rec[-43] rec[-3]
        DETECTOR(8, 7, 0) rec[-42] rec[-2]
        OBSERVABLE_INCLUDE(0) rec[-1]
        SHIFT_COORDS(0, 0, 1)
        TICK
    """)
