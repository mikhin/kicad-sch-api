"""
bulk_update/filter must only touch components that match the criteria.

An unsupported criteria key used to be ignored, so the filter matched every
component and bulk_update rewrote the whole schematic.
"""

import pytest

import kicad_sch_api as ksa


@pytest.fixture
def schematic():
    sch = ksa.create_schematic("bulk_update_criteria")
    for ref, value in [("R1", "10k"), ("R2", "10k"), ("R3", "4k7")]:
        sch.components.add(lib_id="Device:R", reference=ref, value=value, position=(10, 10))
    return sch


def test_filter_by_reference_matches_one(schematic):
    assert [c.reference for c in schematic.components.filter(reference="R2")] == ["R2"]


def test_bulk_update_by_reference_touches_only_that_component(schematic):
    updated = schematic.components.bulk_update(
        criteria={"reference": "R2"}, updates={"value": "22k"}
    )

    assert updated == 1
    assert {c.reference: c.value for c in schematic.components} == {
        "R1": "10k",
        "R2": "22k",
        "R3": "4k7",
    }


def test_unsupported_criteria_raises_instead_of_matching_everything(schematic):
    with pytest.raises(ValueError, match="ref"):
        schematic.components.bulk_update(criteria={"ref": "R2"}, updates={"value": "22k"})

    assert [c.value for c in schematic.components] == ["10k", "10k", "4k7"]
