"""Static checks on the requirements manifests.

The default install takes the whole pyssp stack through one
``pyssp-workflow[sysml,flow]`` direct reference in ``requirements.txt``: the
workflow wheel transitively pins the other seven distributions. The version the
URL names must be the version the workflow source tree declares, so a tag bump
and a filename bump cannot drift apart. The development file composes the
default and replaces each distribution with an editable checkout. No installs
and no network access here.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = REPO_ROOT / "requirements.txt"
DEV_REQUIREMENTS = REPO_ROOT / "requirements-dev.txt"
SYSML_REQUIREMENTS = REPO_ROOT / "requirements-sysml.txt"

#: The one pinned distribution (PEP 503 normalised) -> its editable source tree.
#: The other seven distributions arrive transitively from this wheel.
VENDORED_TREES: dict[str, str] = {
    "pyssp-workflow": "3rd_party/pyssp_workflow",
}

#: The extras the default reference must select: the SysML bundle and the flow
#: engine. Without them the install misses libraries the suite imports.
REQUIRED_EXTRAS = {"sysml", "flow"}

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


def wheel_filename(canonical: str, version: str) -> str:
    """Return the PEP 427 wheel filename for a release asset."""
    return f"{canonical.replace('-', '_')}-{version}-py3-none-any.whl"


def pyproject_version(tree: Path) -> str:
    """Return the distribution version a source tree declares.

    A static ``[project] version`` wins. Trees that declare
    ``dynamic = ["version"]`` are resolved through the
    ``[tool.setuptools.dynamic] version`` attribute, whose module holds the
    literal ``__version__`` assignment.
    """
    pyproject = tree / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data["project"]
    version = project.get("version")
    if version is not None:
        return str(version)
    if "version" not in project.get("dynamic", []):
        raise ValueError(f"{pyproject}: declares no static or dynamic version")
    attribute = data["tool"]["setuptools"]["dynamic"]["version"]["attr"]
    module = str(attribute).split(".")[0]
    for candidate in (
        tree / "src" / module / "__init__.py",
        tree / module / "__init__.py",
    ):
        if not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8")
        match = re.search(
            r"^__version__\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE
        )
        if match:
            return match.group(1)
    raise ValueError(f"{pyproject}: cannot resolve {attribute!r}")


def declared_versions() -> dict[str, str]:
    return {
        canonical: pyproject_version(REPO_ROOT / tree)
        for canonical, tree in VENDORED_TREES.items()
    }


def test_default_requirements_reference_the_bundle_exactly_once() -> None:
    names = [name for name, _ in direct_references(REQUIREMENTS)]
    assert names == ["pyssp-workflow"]


def test_default_requirements_select_the_sysml_and_flow_extras() -> None:
    assert bundle_extras() == REQUIRED_EXTRAS


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


def test_direct_reference_urls_name_the_tree_version() -> None:
    versions = declared_versions()
    wrong: dict[str, str] = {}
    for canonical, url in direct_references(REQUIREMENTS):
        version = versions[canonical]
        expected = wheel_filename(canonical, version)
        if PurePosixPath(urlsplit(url).path).name != expected:
            wrong[url] = expected
        # The release asset lives under a v<version> tag; a tag typo must fail
        # offline rather than at install time.
        if f"/releases/download/v{version}/" not in url:
            wrong[url] = f"/releases/download/v{version}/"
    assert wrong == {}


def test_default_requirements_exclude_the_nested_pinned_copy() -> None:
    # pyssp_sysml2 carries a pinned pyssp-standard copy that imports the same
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


def test_development_requirements_point_at_trees_that_exist() -> None:
    targets = editables(DEV_REQUIREMENTS)
    assert VENDORED_TREES["pyssp-workflow"] in targets
    assert sorted(target for target in targets if not (REPO_ROOT / target).is_dir()) == []


def test_development_requirements_check_out_the_whole_bundle() -> None:
    # Every editable is a checkout inside the one top-level submodule; a
    # repo-level SysML submodule would be a second owner of the same pin.
    targets = editables(DEV_REQUIREMENTS)
    outside = sorted(
        target for target in targets if not target.startswith("3rd_party/pyssp_workflow")
    )
    assert outside == []
    assert {
        "3rd_party/pyssp_workflow/3rd_party/pycps_sysml2",
        "3rd_party/pyssp_workflow/3rd_party/pyfmi_sysml2",
    } <= targets


def test_sysml_requirements_use_no_mirror() -> None:
    options = [
        line for line in requirement_lines(SYSML_REQUIREMENTS) if line.startswith("-")
    ]
    assert not [
        line
        for line in options
        if line.startswith(("--find-links", "--extra-index-url", "-f"))
    ]
