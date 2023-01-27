import functools
from typing import Tuple, Iterable, FrozenSet, Callable

from hookinj.gen._tile import Tile
from hookinj.gen._util import sorted_complex


class Patch:
    """A collection of annotated stabilizers to measure simultaneously.
    """

    def __init__(self,
                 tiles: Iterable[Tile],
                 *,
                 do_not_sort: bool = False):
        if do_not_sort:
            self.tiles = tuple(tiles)
        else:
            self.tiles = tuple(sorted_complex(tiles, key=lambda e: e.measurement_qubit))

    def after_coordinate_transform(self, coord_transform: Callable[[complex], complex]) -> 'Patch':
        return Patch(
            [e.after_coordinate_transform(coord_transform) for e in self.tiles],
        )

    def after_basis_transform(self, basis_transform: Callable[[str], str]) -> 'Patch':
        return Patch(
            [e.after_basis_transform(basis_transform) for e in self.tiles],
        )

    def with_opposite_order(self) -> 'Patch':
        return Patch(tiles=[
            Tile(
                bases=tile.bases[::-1],
                measurement_qubit=tile.measurement_qubit,
                ordered_data_qubits=tile.ordered_data_qubits[::-1],
            )
            for tile in self.tiles
        ])

    @functools.cached_property
    def used_set(self) -> FrozenSet[complex]:
        result = set()
        for e in self.tiles:
            result |= e.used_set
        return frozenset(result)

    @functools.cached_property
    def data_set(self) -> FrozenSet[complex]:
        result = set()
        for e in self.tiles:
            for q in e.ordered_data_qubits:
                if q is not None:
                    result.add(q)
        return frozenset(result)

    def __eq__(self, other):
        if not isinstance(other, Patch):
            return NotImplemented
        return self.tiles == other.tiles

    def __ne__(self, other):
        return not (self == other)

    @functools.cached_property
    def measure_set(self) -> FrozenSet[complex]:
        return frozenset(e.measurement_qubit for e in self.tiles)

    def bounding_box(self, extras: Iterable[complex] = ()) -> Tuple[complex, complex]:
        qs = self.used_set | set(extras)
        min_r = min((e.real for e in qs), default=0)
        min_i = min((e.imag for e in qs), default=0)
        max_r = max((e.real for e in qs), default=0)
        max_i = max((e.imag for e in qs), default=0)
        return min_r + min_i * 1j, max_r + max_i * 1j
