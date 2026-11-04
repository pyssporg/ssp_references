"""Static policy for the root suite: skip guards and tracked writes.

Two rules are decidable from the test sources and are enforced here:

1. A ``pytest.skip`` guarded by a missing artifact or a missing engine must
   name the remedy (a ``scripts/...`` command or an install hint), otherwise a
   broken checkout reads as a green run.
2. The suite may not write into tracked paths. A write target is judged safe
   only when it resolves to a ``tmp_path``/``tmpdir`` local; targets that
   resolve to ``REPO_ROOT``/``__file__`` or a repo-relative literal fail.
   Targets whose dataflow crosses a helper parameter are undecidable statically
   and are not asserted (they are reported in the message of a failing check
   only when they would otherwise be judged).

Also: no committed non-``.py`` file under ``tests/`` may go undocumented in
``tests/README.md``.
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent

ARTIFACT_GUARD_TOKENS = (
    ".is_file(",
    ".is_dir(",
    ".exists(",
    "omsimulator",
    "ssp4sim",
    "fmpy",
    "engine",
)

REMEDY_TOKENS = (
    "scripts/",
    "build_models.py",
    "run_simulations.py",
    "run_comparisons.py",
    "run simulations",
    "run comparisons",
    "pip install",
    "install",
)

TRACKED_PATH_TOKENS = (
    "REPO_ROOT",
    "__file__",
    "artifacts/",
    "models/",
    "scripts/",
    "tests/",
)


def _is_pytest_skip(func: ast.expr) -> bool:
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "skip"
        and isinstance(func.value, ast.Name)
        and func.value.id == "pytest"
    )


def _guards_on_artifacts(test: ast.expr) -> bool:
    source = ast.unparse(test)
    return any(token in source for token in ARTIFACT_GUARD_TOKENS)


def _message(call: ast.Call) -> str:
    parts = [ast.unparse(arg) for arg in call.args]
    parts.extend(ast.unparse(keyword.value) for keyword in call.keywords)
    return " ".join(parts)


def _skip_violations(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[str] = []

    def visit(node: ast.AST, guards: list[ast.If]) -> None:
        if isinstance(node, ast.If):
            guards = [*guards, node]
        if (
            isinstance(node, ast.Call)
            and _is_pytest_skip(node.func)
            and any(_guards_on_artifacts(guard.test) for guard in guards)
        ):
            message = _message(node).lower()
            if not any(token in message for token in REMEDY_TOKENS):
                violations.append(f"{path.name}:{node.lineno}: skip without remedy: {_message(node)}")
        for child in ast.iter_child_nodes(node):
            visit(child, guards)

    visit(tree, [])
    return violations


def _tmp_derived_names(function: ast.AST) -> set[str]:
    assignments: dict[str, str] = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            source = ast.unparse(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = source
    derived = {"tmp_path", "tmpdir"}
    changed = True
    while changed:
        changed = False
        for name, source in assignments.items():
            if name in derived:
                continue
            if any(token in source for token in derived):
                derived.add(name)
                changed = True
    return derived


def _write_targets(node: ast.AST) -> list[str]:
    if not isinstance(node, ast.Call):
        return []
    func = node.func
    if isinstance(func, ast.Attribute) and func.attr in {"write_text", "write_bytes"}:
        return [ast.unparse(func.value)]
    is_open = (isinstance(func, ast.Name) and func.id == "open") or (
        isinstance(func, ast.Attribute) and func.attr == "open"
    )
    if (
        is_open
        and len(node.args) >= 2
        and isinstance(node.args[1], ast.Constant)
        and any(flag in str(node.args[1].value) for flag in "wax+")
    ):
        return [ast.unparse(node.args[0])]
    return []


def _tracked_writes(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    violations: list[str] = []

    scopes = [tree, *(node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)))]
    for scope in scopes:
        derived = _tmp_derived_names(scope)
        for node in ast.walk(scope):
            for target in _write_targets(node):
                if any(token in target for token in derived):
                    continue
                if any(token in target for token in TRACKED_PATH_TOKENS):
                    violations.append(f"{path.name}:{node.lineno}: write into tracked path: {target}")
    return list(dict.fromkeys(violations))


def test_artifact_skips_name_a_remedy() -> None:
    violations: list[str] = []
    for path in sorted(TESTS_DIR.glob("*.py")):
        violations.extend(_skip_violations(path))
    assert violations == [], "\n".join(violations)


def test_no_test_writes_into_tracked_paths() -> None:
    violations: list[str] = []
    for path in sorted(TESTS_DIR.glob("*.py")):
        violations.extend(_tracked_writes(path))
    assert violations == [], "\n".join(violations)


def test_non_python_fixtures_are_documented() -> None:
    readme = TESTS_DIR / "README.md"
    assert readme.is_file(), "tests/README.md is missing"
    documented = readme.read_text(encoding="utf-8")

    undocumented = [
        path.relative_to(TESTS_DIR).as_posix()
        for path in sorted(TESTS_DIR.rglob("*"))
        if path.is_file()
        and path.name != "README.md"
        and path.suffix != ".py"
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and path.name not in documented
    ]
    assert undocumented == [], f"undocumented fixtures under tests/: {undocumented}"
