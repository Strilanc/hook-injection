import dataclasses
import pathlib
from typing import Union, Any, Optional, List, Callable, Dict

import stim

from hookinj import gen
from hookinj.circuits._cphase_injection_circuit import make_zz_injection
from hookinj.circuits._hook_injection_circuit import make_hook_injection_circuit
from hookinj.circuits._li_injection_circuit import make_li_injection_rounds
from hookinj.circuits._xz_memory_circuits import make_xz_memory_experiment_chunks
from hookinj.circuits._y_memory_circuit import make_y_memory_experiment_chunks


def _write(path: Any, content: Any):
    path = pathlib.Path(path)
    with open(path, "w") as f:
        print(content, file=f)
    print(f'wrote file://{path.absolute()}')


@dataclasses.dataclass
class Params:
    basis: str
    postselected_rounds: int
    postselected_diameter: int
    memory_rounds: int
    distance: int

    def no_postselection(self):
        assert self.postselected_rounds == 0
        assert self.postselected_diameter == 0
        return self


def _make_constructions() -> Dict[str, Callable[[Params], List[gen.Chunk]]]:
    constructions: Dict[str, Callable[[Params], List[gen.Chunk]]] = {}

    constructions['X'] = lambda params: make_xz_memory_experiment_chunks(
        basis='X',
        distance=params.no_postselection().distance,
        memory_rounds=params.memory_rounds,
    )
    constructions['Z'] = lambda params: make_xz_memory_experiment_chunks(
        basis='Z',
        distance=params.no_postselection().distance,
        memory_rounds=params.memory_rounds,
    )
    constructions['Y'] = lambda params: make_y_memory_experiment_chunks(
        distance=params.no_postselection().distance,
        memory_rounds=params.memory_rounds,
    )

    def add_hook(basis: str, pregrow: bool, magic: bool):
        if basis == 'Z':
            return
        name = 'pregrown_hook' if pregrow else 'hook'
        suffix = '_magic_verify' if magic else ''
        constructions[f'{name}_inject_{basis}{suffix}'] = lambda params: make_hook_injection_circuit(
            distance=params.distance,
            postselected_rounds=params.postselected_rounds,
            postselected_diameter=params.postselected_diameter,
            memory_rounds=params.memory_rounds,
            injection_basis=basis,
            magic_measurement=magic,
            start_full=pregrow,
        )
    def add_li(basis: str):
        constructions[f'li_inject_{basis}_magic_verify'] = lambda params: make_li_injection_rounds(
            distance=params.distance,
            postselected_rounds=params.postselected_rounds,
            postselected_diameter=params.postselected_diameter,
            memory_rounds=params.memory_rounds,
            injection_basis=basis,
            magic_measurement=True,
        )
        if basis == 'Y':
            return
        constructions[f'li_inject_{basis}'] = lambda params: make_li_injection_rounds(
            distance=params.distance,
            postselected_rounds=params.postselected_rounds,
            postselected_diameter=params.postselected_diameter,
            memory_rounds=params.memory_rounds,
            injection_basis=basis,
            magic_measurement=False,
        )
    def add_zz(basis: str, tweaked: bool):
        if basis == 'Z':
            return
        name = 'zz_tweaked' if tweaked else 'zz'
        constructions[f'{name}_inject_{basis}_magic_verify'] = lambda params: make_zz_injection(
            distance=params.distance,
            postselected_rounds=params.postselected_rounds,
            postselected_diameter=params.postselected_diameter,
            memory_rounds=params.memory_rounds,
            injection_basis=basis,
            magic_measurement=True,
            tweaked=tweaked,
        )
        if basis == 'Y':
            return
        constructions[f'{name}_inject_{basis}'] = lambda params: make_zz_injection(
            distance=params.distance,
            postselected_rounds=params.postselected_rounds,
            postselected_diameter=params.postselected_diameter,
            memory_rounds=params.memory_rounds,
            injection_basis=basis,
            magic_measurement=False,
            tweaked=tweaked,
        )

    for b in 'XYZ':
        for p in [False, True]:
            for m in [False, True]:
                add_hook(b, p, m)
        add_li(b)
        for t in [False, True]:
            add_zz(b, t)

    return constructions


CONSTRUCTIONS = _make_constructions()


def make_circuit(
    *,
    basis: str,
    noise: Optional[gen.NoiseModel],
    postselected_rounds: int = 0,
    postselected_diameter: int = 0,
    memory_rounds: int,
    distance: int,
    verify_chunks: bool = False,
    debug_out_dir: Union[None, str, pathlib.Path] = None,
    convert_to_cz: bool = True,
) -> stim.Circuit:
    params = Params(basis=basis, postselected_rounds=postselected_rounds, postselected_diameter=postselected_diameter, memory_rounds=memory_rounds, distance=distance)
    construction = CONSTRUCTIONS.get(basis)
    if construction is None:
        raise NotImplementedError(f'{basis=}')
    chunks = construction(params)

    assert len(chunks) >= 2
    if 'magic' not in basis:
        assert not any(chunk.magic for chunk in chunks)

    if debug_out_dir is not None:
        patches = [chunk.end_patch() for chunk in chunks[:-1]]
        changed_patches = [patches[k] for k in range(len(patches)) if k == 0 or patches[k] != patches[k-1]]
        allowed_qubits = {q for patch in changed_patches for q in patch.used_set}
        _write(debug_out_dir / "patch.svg", gen.patch_svg_viewer(
            changed_patches,
            show_order=False,
            available_qubits=allowed_qubits,
        ))

    if verify_chunks:
        for chunk in chunks:
            chunk.verify()

    if debug_out_dir is not None:
        ignore_errors_ideal_circuit = gen.compile_chunks_into_circuit(chunks, ignore_errors=True)
        _write(debug_out_dir / "ideal_circuit.html", gen.stim_circuit_html_viewer(
            ignore_errors_ideal_circuit,
            patch={k: chunks[k].end_patch() for k in range(len(chunks))},
        ))
        _write(debug_out_dir / "ideal_circuit.stim", ignore_errors_ideal_circuit)
        _write(debug_out_dir / "ideal_circuit_dets.svg", ignore_errors_ideal_circuit.diagram("time+detector-slice-svg"))

    body = gen.compile_chunks_into_circuit(chunks)
    mpp_indices = [
        k
        for k, inst in enumerate(body)
        if isinstance(inst, stim.CircuitInstruction) and inst.name == 'MPP'
    ]
    skip_mpp_head = chunks[0].magic
    skip_mpp_tail = chunks[-1].magic
    body_start = mpp_indices[0] + 2 if skip_mpp_head else 0
    body_end = mpp_indices[-1] if skip_mpp_tail else len(body)
    magic_head = body[:body_start]
    magic_tail = body[body_end:]
    body = body[body_start:body_end]

    if convert_to_cz:
        body = gen.to_z_basis_interaction_circuit(body)
        if debug_out_dir is not None:
            ideal_circuit = magic_head + body + magic_tail
            _write(debug_out_dir / "ideal_cz_circuit.html", gen.stim_circuit_html_viewer(
                ideal_circuit,
                patch=chunks[0].end_patch(),
            ))
            _write(debug_out_dir / "ideal_cz_circuit.stim", ideal_circuit)
            _write(debug_out_dir / "ideal_cz_circuit_dets.svg", ideal_circuit.diagram("time+detector-slice-svg"))

    if noise is not None:
        body = noise.noisy_circuit(body)
    noisy_circuit = magic_head + body + magic_tail

    if debug_out_dir is not None:
        _write(debug_out_dir / "noisy_circuit.html", gen.stim_circuit_html_viewer(
            noisy_circuit,
            patch=chunks[0].end_patch(),
        ))
        _write(debug_out_dir / "noisy_circuit.stim", noisy_circuit)
        _write(debug_out_dir / "noisy_circuit_dets.svg", noisy_circuit.diagram("time+detector-slice-svg"))

    return noisy_circuit
