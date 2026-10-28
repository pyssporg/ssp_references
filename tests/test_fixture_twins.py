"""Fixture twins: the canonical set against the pinned copy.

The pinned ``pyssp_sysml2/3rd_party/pyssp_standard`` checkout keeps its own
``pytest/__fixture__`` copy of the same EMBRACE example, ~5.8 MB duplicated on
disk. It is a dependency, not editable here, so the copy can only drift away
from the canonical one silently.

One divergence is known and documented: the pinned ``mixed_example.ssd`` is a
*serialized* variant, written by an older codec, so its bytes differ while its
model is the same. Every other fixture must be byte-identical. A new difference
is a red test, not a surprise.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

WORKFLOW = Path(__file__).resolve().parents[1] / "3rd_party" / "pyssp_workflow"
CANONICAL = WORKFLOW / "3rd_party" / "pyssp_standard" / "tests" / "fixtures"
PINNED = (
    WORKFLOW
    / "3rd_party"
    / "pyssp_sysml2"
    / "3rd_party"
    / "pyssp_standard"
    / "pytest"
    / "__fixture__"
)

#: Canonical case file -> pinned file name. The canonical set names cases after
#: the behaviour; the pinned copy keeps the historical flat names.
TWINS = {
    "ssv-external-parameter-set/input.ssv": "external_values.ssv",
    "ssv2-typed-parameters/input.ssv": "ssv2_ex.ssv",
    "srmd-easyssp-sample/input.srmd": "test_schema_validation.srmd",
    "payload-plain-text/input.txt": "test.txt",
}

#: Provenance notes live with the canonical case only; the pinned copy has none.
DOCUMENTATION = frozenset({"case.md", "README.md"})

#: The one documented divergence: same model, different serialization.
SERIALIZED_TWIN = "ssd-mixed-parameter-bindings/input.ssd"
SERIALIZED_TWIN_NAME = "mixed_example.ssd"


def _normalized(xml_text: str) -> tuple:
    """Namespace-free, whitespace-free tree, with binding prefixes undotted."""
    root = ET.fromstring(xml_text)

    def walk(element: ET.Element) -> tuple:
        attributes = []
        for name, value in element.attrib.items():
            key = name.split("}")[-1]
            if key == "prefix" and value.endswith("."):
                value = value[:-1]
            attributes.append((key, value))
        return (
            element.tag.split("}")[-1],
            tuple(sorted(attributes)),
            (element.text or "").strip(),
            tuple(walk(child) for child in element),
        )

    return walk(root)


@pytest.mark.parametrize("case_name", sorted(TWINS), ids=lambda name: name.split("/")[0])
def test_pinned_twin_is_byte_identical(case_name: str) -> None:
    canonical = CANONICAL / case_name
    pinned = PINNED / TWINS[case_name]

    assert canonical.is_file(), f"missing canonical fixture: {canonical}"
    assert pinned.is_file(), f"missing pinned fixture: {pinned}"
    assert canonical.read_bytes() == pinned.read_bytes()


def test_serialized_twin_differs_only_in_serialization() -> None:
    canonical = CANONICAL / SERIALIZED_TWIN
    pinned = PINNED / SERIALIZED_TWIN_NAME

    assert canonical.read_bytes() != pinned.read_bytes(), (
        "the pinned copy caught up with the canonical fixture; delete this case "
        "from the divergence allowlist instead of keeping a stale exception"
    )
    assert _normalized(canonical.read_text(encoding="utf-8")) == _normalized(
        pinned.read_text(encoding="utf-8")
    ), "the pinned serialized variant no longer describes the canonical model"


def test_pinned_copy_has_no_fixture_outside_the_mapped_set() -> None:
    mapped = set(TWINS.values()) | {SERIALIZED_TWIN_NAME}
    unmapped = sorted(
        path.name
        for path in PINNED.iterdir()
        if path.is_file() and path.name not in mapped
    )

    assert unmapped == [], f"unmapped fixtures in the pinned copy: {unmapped}"


def test_embrace_fixture_trees_match() -> None:
    canonical = CANONICAL / "embrace"
    pinned = PINNED / "embrace"

    canonical_files = sorted(
        path.relative_to(canonical)
        for path in canonical.rglob("*")
        if path.is_file() and path.name not in DOCUMENTATION
    )
    pinned_files = sorted(
        path.relative_to(pinned)
        for path in pinned.rglob("*")
        if path.is_file() and path.name not in DOCUMENTATION
    )

    assert canonical_files == pinned_files
    for relative in canonical_files:
        assert (canonical / relative).read_bytes() == (pinned / relative).read_bytes(), (
            f"EMBRACE fixture drifted: {relative}"
        )
