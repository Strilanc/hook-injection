import pytest
import stim

from hookinj import gen


def test_verify_h():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            H 0
        """),
        q2i={1j: 0},
        flows=[gen.Flow(
            center=0,
            start=gen.PauliString({1j: 'X'}),
            end=gen.PauliString({1j: 'Z'}),
        )],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            H 0
        """),
        q2i={1j: 0},
        flows=[gen.Flow(
            center=0,
            start=gen.PauliString({1j: 'X'}),
            end=gen.PauliString({1j: 'Y'}),
        )],
    )
    with pytest.raises(ValueError):
        chunk.verify()


def test_verify_r():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            R 0
        """),
        q2i={1j: 0},
        flows=[gen.Flow(
            center=0,
            start=gen.PauliString({1j: 'Z'}),
            end=gen.PauliString({}),
        )],
    )
    with pytest.raises(ValueError):
        chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            R 0
        """),
        q2i={1j: 0},
        flows=[gen.Flow(
            center=0,
            start=gen.PauliString({}),
            end=gen.PauliString({1j: 'Z'}),
        )],
    )
    chunk.verify()


def test_verify_measurement():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            R 1
            CX 0 1 2 1
            M 1 3
            H 0
        """),
        q2i={0: 0, 1j: 1, 2j: 2, 3j: 3},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'Z', 2j: 'Z'}),
                measurement_indices=[0],
            ),
            gen.Flow(
                center=0,
                end=gen.PauliString({0: 'X', 2j: 'Z'}),
                measurement_indices=[0],
            ),
        ],
    )
    chunk.verify()


def test_verify_mpp():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            MPP X0*Y1*Z2
        """),
        q2i={0: 0, 1j: 1, 2j: 2, 3j: 3},
        flows=[
            gen.Flow(
                center=0,
                end=gen.PauliString({0: 'X', 1j: 'Y', 2j: 'Z'}),
                measurement_indices=[0],
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            MPP X0*Y1*Z2
            MPP X0*X1*Z2
        """),
        q2i={0: 0, 1j: 1, 2j: 2, 3j: 3},
        flows=[
            gen.Flow(
                center=0,
                end=gen.PauliString({0: 'X', 1j: 'Y', 2j: 'Z'}),
                measurement_indices=[0],
            ),
        ],
    )
    with pytest.raises(ValueError, match='Anticommuted with MPP'):
        chunk.verify()


def test_verify_c_xyz():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            C_XYZ 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'Y', 1: 'Z', 2: 'X'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            C_ZYX 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'Z', 1: 'X', 2: 'Y'}),
            ),
        ],
    )
    chunk.verify()


def test_verify_s():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            S 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'Y', 1: 'X', 2: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            S_DAG 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'Y', 1: 'X', 2: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            H_XY 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'Y', 1: 'X', 2: 'Z'}),
            ),
        ],
    )
    chunk.verify()


def test_verify_sqrt_x():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            SQRT_X 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'X', 1: 'Z', 2: 'Y'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            SQRT_X_DAG 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'X', 1: 'Z', 2: 'Y'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            H_YZ 0 1 2
        """),
        q2i={0: 0, 1: 1, 2: 2},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Z'}),
                end=gen.PauliString({0: 'X', 1: 'Z', 2: 'Y'}),
            ),
        ],
    )
    chunk.verify()


def test_verify_cy():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            CY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'Y', 2: 'Y', 3: 'Y', 4: 'Z'}),
                end=gen.PauliString({0: 'X', 2: 'Y', 4: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            CY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 2: 'Y', 4: 'Z'}),
                end=gen.PauliString({0: 'X', 1: 'Y', 2: 'Y', 3: 'Y', 4: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            CY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'X', 2: 'Y', 3: 'X', 4: 'Z', 5: 'X'}),
                end=gen.PauliString({0: 'Y', 1: 'Z', 2: 'X', 3: 'Z', 5: 'X'}),
            ),
        ],
    )
    chunk.verify()


@pytest.mark.parametrize('gate', [
    'I',
    'X',
    'Y',
    'Z',
    'C_XYZ',
    'C_ZYX',
    'H',
    'H_XY',
    'H_XZ',
    'H_YZ',
    'S',
    'SQRT_X',
    'SQRT_X_DAG',
    'SQRT_Y',
    'SQRT_Y_DAG',
    'SQRT_Z',
    'SQRT_Z_DAG',
    'S_DAG',
    'CNOT',
    'CX',
    'CY',
    'CZ',
    'ISWAP',
    'ISWAP_DAG',
    'SQRT_XX',
    'SQRT_XX_DAG',
    'SQRT_YY',
    'SQRT_YY_DAG',
    'SQRT_ZZ',
    'SQRT_ZZ_DAG',
    'SWAP',
    'XCX',
    'XCY',
    'XCZ',
    'YCX',
    'YCY',
    'YCZ',
    'ZCX',
    'ZCY',
    'ZCZ',
])
def test_verify_gate_flows_vs_stim_tableau(gate: str):
    circuit = stim.Circuit(f'{gate} 0 1')
    tableau = stim.Tableau.from_circuit(circuit)
    flows = []
    if len(tableau) == 2:
        for p0 in 'IXYZ':
            for p1 in 'IXYZ':
                i = stim.PauliString(p0 + p1)
                flows.append((i, tableau(i)))
    elif len(tableau) == 1:
        for p0 in 'IXYZ':
            i = stim.PauliString(p0)
            flows.append((i, tableau(i)))
    else:
        raise NotImplementedError()
    for flow in flows:
        chunk = gen.Chunk(
            circuit=circuit,
            q2i={0: 0, 1: 1},
            flows=[
                gen.Flow(
                    center=0,
                    start=gen.PauliString.from_stim_pauli_string(flow[0]),
                    end=gen.PauliString.from_stim_pauli_string(flow[1]),
                    allow_vacuous=True,
                ),
            ],
        )
        chunk.verify()


def test_verify_swap():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            SWAP 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 2: 'Y', 3: 'Y', 4: 'Z', 5: 'Y'}),
                end=gen.PauliString({1: 'X', 3: 'Y', 2: 'Y', 5: 'Z', 4: 'Y'}),
            ),
        ],
    )
    chunk.verify()


def test_verify_xcy():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            XCY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 2: 'Y', 3: 'Y', 4: 'Z', 5: 'Y'}),
                end=gen.PauliString({0: 'X', 2: 'Y', 4: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            YCX 1 0 3 2 5 4
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 2: 'Y', 3: 'Y', 4: 'Z', 5: 'Y'}),
                end=gen.PauliString({0: 'X', 2: 'Y', 4: 'Z'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            XCY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 2: 'Y', 4: 'Z'}),
                end=gen.PauliString({0: 'X', 2: 'Y', 3: 'Y', 4: 'Z', 5: 'Y'}),
            ),
        ],
    )
    chunk.verify()

    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            XCY 0 1 2 3 4 5
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({0: 'X', 1: 'X', 2: 'Y', 3: 'X', 4: 'Z', 5: 'X'}),
                end=gen.PauliString({1: 'X', 2: 'Z', 3: 'Z', 4: 'Y', 5: 'Z'}),
            ),
        ],
    )
    chunk.verify()


def test_reset_analysis():
    chunk = gen.Chunk(
        circuit=stim.Circuit("""
            R 0 1 2 3 4
            CX 2 0
            M 0
        """),
        q2i={0: 0, 1: 1, 2: 2, 3: 3, 4: 4},
        flows=[
            gen.Flow(
                center=0,
                start=gen.PauliString({}),
                measurement_indices=[0],
                end=gen.PauliString({1: 'Z'}),
            ),
        ],
    )
    f = gen.FlowStabilizerVerifier.verify(chunk)
    assert f.reset_to_flow_indices == {2: [0], 3: [0], 4: [0]}

    inverted = gen.FlowStabilizerVerifier.invert(chunk)
    inverted.verify()
    assert len(inverted.flows) == len(chunk.flows)
    assert inverted.circuit == stim.Circuit("""
        R 0
        CX 2 0
        M 4 3 2 1 0
    """)
