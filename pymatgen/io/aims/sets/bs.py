"""Input sets for band structure calculations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict

from pymatgen.core import Structure
from pymatgen.io.aims.sets.base import AimsInputGenerator
from pymatgen.symmetry.bandstructure import HighSymmKpath

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pymatgen.core import Molecule

__author__ = "Andrey Sobolev and Thomas A. R. Purcell"
__version__ = "1.0"
__email__ = "andrey.n.sobolev@gmail.com and purcellt@arizona.edu"
__date__ = "November 2023"


@dataclass
class BandStructureSetGenerator(AimsInputGenerator):
    """A generator for the band structure calculation input set.

    Parameters
    ----------
    calc_type: str
        The type of calculations
    k_point_density: float
        The number of k_points per angstrom
    """

    calc_type: str = "bands"
    k_point_density: float = 20

    def get_parameter_updates(self, structure: Structure, prev_parameters: dict[str, Any]) -> dict[str, Sequence[str]]:
        """Get the parameter updates for the calculation.

        Parameters
        ----------
        structure: Structure
            The structure to calculate the bands for
        prev_parameters: Dict[str, Any]
            The previous parameters

        Returns
        -------
        The updated for the parameters for the output section of FHI-aims
        """
        updated_outputs = prev_parameters.get("output", [])
        updated_outputs += _prepare_band_input(structure, self.k_point_density)
        return {"output": updated_outputs}


@dataclass
class GWSetGenerator(AimsInputGenerator):
    """
    A generator for the input set for calculations employing GW self-energy correction.

    Parameters
    ----------
    calc_type: str
        The type of calculations
    k_point_density: float
        The number of k_points per angstrom
    """

    calc_type: str = "GW"
    k_point_density: float = 20

    def get_parameter_updates(self, structure: Structure | Molecule, prev_parameters: dict[str, Any]) -> dict[str, Any]:
        """Get the parameter updates for the calculation.

        Parameters
        ----------
        structure: Structure or Molecule
            The structure to calculate the bands for
        prev_parameters: Dict[str, Any]
            The previous parameters

        Returns
        -------
        The updated for the parameters for the output section of FHI-aims
        """
        updates = {"anacon_type": "two-pole"}
        current_output = prev_parameters.get("output", [])
        if isinstance(structure, Structure) and all(structure.lattice.pbc):
            updates.update(
                {
                    "qpe_calc": "gw_expt",
                    "output": current_output + _prepare_band_input(structure, self.k_point_density),
                }
            )
        else:
            updates.update(
                {
                    "qpe_calc": "gw",
                }
            )
        return updates


class _SegmentDict(TypedDict):
    coords: list[list[float]]
    labels: list[str]
    length: int


def _prepare_band_input(structure: Structure, density: float = 20):
    """Prepare the band information needed for the FHI-aims control.in file.

    Parameters
    ----------
    structure: Structure
        The structure for which the band path is calculated
    density: float
        Number of kpoints per Angstrom.
    """
    bp = HighSymmKpath(structure)
    points, labels = bp.get_kpoints(line_density=density, coords_are_cartesian=False)
    lines_and_labels: list[_SegmentDict] = []
    current_segment: _SegmentDict = _SegmentDict(coords=[], labels=[], length=0)
    for label_, coords in zip(labels, points):
        # rename the Gamma point label
        label = "G" if label_ in ("GAMMA", "\\Gamma", "Γ") else label_
        current_segment["length"] += 1
        if label:
            current_segment["coords"].append(coords)
            current_segment["labels"].append(label)
            if current_segment["length"] > 1:
                lines_and_labels.append(current_segment)
                current_segment = _SegmentDict(coords=[], labels=[], length=0)

    bands = []
    for segment in lines_and_labels:
        start, end = segment["coords"]
        lstart, lend = segment["labels"]
        bands.append(
            f"band {start[0]:9.5f}{start[1]:9.5f}{start[2]:9.5f} "
            f"{end[0]:9.5f}{end[1]:9.5f}{end[2]:9.5f} {segment['length']:4d} "
            f"{lstart:3}{lend:3}"
        )
    return bands
