"""Static checks on the requirements manifests.

``requirements.txt`` is this repository's default install contract: one plain
``pyssp-workflow`` direct reference brings the whole pyssp stack as base
dependencies, and ``requirements-dev.txt`` composes it. These checks keep the
manifests internally consistent — a single direct reference, no extras, no
mirror, no committed editables — with no installs and no network access.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = REPO_ROOT / "requirements.txt"
DEV_REQUIREMENTS = REPO_ROOT / "requirements-dev.txt"
SYSML_REQUIREMENTS = REPO_ROOT / "requirements-sysml.txt"

# ``name[extra] @ url``; a bare URL or an option line never has this shape.
_DIRECT_REFERENCE = re.compile(
    r"^(?P<name>[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"\s*(?:\[(?P<extras>[^\]]*)\])?\s*@\s*(?P<url>[^\s;]+)$"
)


def canonical_name(name: str) -> str:
    """Return the PEP 503 name used by both requirement lines and wheel files."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def requirement_lines(path: Path) -> list[str]:
    """Return the non-blank, non-comment lines of a requirements file."""
    return [
        line
        for raw in path.read_text(encoding="utf-8").splitlines()
        if (line := raw.split("#", 1)[0].strip())
    ]


def direct_references(path: Path) -> list[tuple[str, str]]:
    """Return ``(canonical name, url)`` for every ``name @ url`` line."""
    references: list[tuple[str, str]] = []
    for line in requirement_lines(path):
        match = _DIRECT_REFERENCE.match(line)
        if match is not None:
            references.append((canonical_name(match.group("name")), match.group("url")))
    return references


def bundle_extras() -> set[str]:
    """Return the extras selected by the default requirements reference."""
    for line in requirement_lines(REQUIREMENTS):
        match = _DIRECT_REFERENCE.match(line)
        if match is not None:
            extras = match.group("extras") or ""
            return {extra.strip() for extra in extras.split(",") if extra.strip()}
    raise AssertionError(f"{REQUIREMENTS}: carries no direct reference")


def editables(path: Path) -> set[str]:
    """Return the checkout paths that ``-e`` / ``--editable`` selects."""
    targets: set[str] = set()
    for line in requirement_lines(path):
        for prefix in ("-e ", "--editable "):
            if line.startswith(prefix):
                targets.add(line[len(prefix) :].strip().removeprefix("./"))
    return targets


def test_default_requirements_reference_the_bundle_exactly_once() -> None:
    names = [name for name, _ in direct_references(REQUIREMENTS)]
    assert names == ["pyssp-workflow"]


def test_default_requirements_select_no_extras() -> None:
    # Every former feature extra is folded into the base dependencies; an
    # extras suffix here would name an extra that no longer exists.
    assert bundle_extras() == set()


def test_default_requirements_are_not_editable_and_use_no_mirror() -> None:
    options = [
        line for line in requirement_lines(REQUIREMENTS) if line.startswith("-")
    ]
    assert not [line for line in options if line.startswith(("-e", "--editable"))]
    assert not [
        line
        for line in options
        if line.startswith(("--find-links", "--extra-index-url", "-f"))
    ]


def test_default_requirements_exclude_the_nested_pinned_copy() -> None:
    # pyssp_sysml2 carried a pinned pyssp-standard copy that imports the same
    # pyssp_standard package; installing it next to the fork would collide.
    names = {name for name, _ in direct_references(REQUIREMENTS)}
    assert "pyssp-standard" not in names


def test_development_requirements_compose_the_default() -> None:
    options = [
        line for line in requirement_lines(DEV_REQUIREMENTS) if line.startswith("-")
    ]
    assert "-r requirements.txt" in options
    assert not [
        line
        for line in options
        if line.startswith(("--find-links", "--extra-index-url", "-f"))
    ]
    assert direct_references(DEV_REQUIREMENTS) == []


def test_development_requirements_contain_no_vendored_editables() -> None:
    # The vendored 3rd_party/pyssp_workflow tree is gone. Development installs
    # each sibling as an editable checkout from the flat ecosystem workspace
    # (pip install -e ../<sibling> in pyssp_dev/repos/), documented as comments
    # rather than committed -e lines, so no editable survives here.
    targets = editables(DEV_REQUIREMENTS)
    assert targets == set()
    assert not any("3rd_party" in target for target in targets)


def test_sysml_requirements_use_no_mirror() -> None:
    options = [
        line for line in requirement_lines(SYSML_REQUIREMENTS) if line.startswith("-")
    ]
    assert not [
        line
        for line in options
        if line.startswith(("--find-links", "--extra-index-url", "-f"))
    ]