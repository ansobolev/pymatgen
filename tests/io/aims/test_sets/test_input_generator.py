"""Tests for the FHI-aims input set generator"""

from __future__ import annotations

from pathlib import Path

import pytest
from pymatgen.io.aims.sets.base import AimsInputGenerator
from pymatgen.util.testing.aims import Si, check_control

module_dir = Path(__file__).resolve().parents[1]
species_dir = module_dir / "species_directory"


def test_input_generator(mocker):
    # Mock default species directory
    from pymatgen.io.aims import inputs

    mocker.patch.object(inputs, "SETTINGS", {"AIMS_SPECIES_DIR": species_dir / "light"})

    # No structure
    with pytest.raises(ValueError, match="No structure can be determined"):
        AimsInputGenerator().get_input_set()

    # default keywords
    generator = AimsInputGenerator(species_dir=species_dir / "tight")
    assert "tight" in generator.get_input_set(Si).control_in
    assert "12 12 12" in generator.get_input_set(Si).control_in
    generator = AimsInputGenerator(k_grid=[8, 8, 8])
    assert "8 8 8" in generator.get_input_set(Si).control_in

    # `use_` and `auto_`-keywords
    Si.set_charge(0.5)
    generator = AimsInputGenerator(use_symmetry=True, auto_mix_param=True, use_structure_charge=True)
    control_in = generator.get_input_set(Si).control_in
    assert check_control("rsly_symmetry", "all", control_in)
    assert check_control("charge_mix_param", 0.3, control_in)
    assert check_control("charge", 0.5, control_in)

    # input set keyword arguments
    generator = AimsInputGenerator()
    control_in = generator.get_input_set(
        Si, input_set_kwargs=dict(species_dir=species_dir / "tight", k_grid=[8, 8, 8])
    ).control_in
    assert "tight" in control_in
    assert "8 8 8" in control_in


def test_input_generator_xc(mocker):
    # Mock default species directory
    from pymatgen.io.aims import inputs

    mocker.patch.object(inputs, "SETTINGS", {"AIMS_SPECIES_DIR": species_dir / "light"})

    assert "pbe0" in AimsInputGenerator(xc="pbe0").get_input_set(Si).control_in
    assert "pbe0" in AimsInputGenerator(xc=dict(name="pbe0")).get_input_set(Si).control_in

    with pytest.raises(ValueError, match="Add `name` key to `xc`"):
        AimsInputGenerator(xc=dict(Name="pbe0")).get_input_set(Si)
    with pytest.raises(ValueError, match="Add `omega` and `unit` to `xc`"):
        AimsInputGenerator(xc="hse06").get_input_set(Si)
    with pytest.raises(ValueError, match="Add `omega` and `unit` to `xc`"):
        AimsInputGenerator(xc=dict(name="hse06", omega=0.11)).get_input_set(Si)
    xc_entry = {"name": "hse06", "omega": 0.11, "unit": "bohr"}
    assert "hse06    0.11" in AimsInputGenerator(xc=xc_entry).get_input_set(Si).control_in
