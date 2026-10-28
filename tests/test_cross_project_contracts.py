"""Cross-project contracts: the hand-written seams between vendored projects.

Each seam is an edge no project owns alone, and each has rotted once already:
``pyssp_simulate``'s fixture used an API ``pyssp_standard`` had removed, and a
``MetricRow`` written by one project could not be judged by another. These tests
pin the edges with both sides real -- no mocks, no engines, no network.

The rule for every test here: the docstring names the drift it catches, and
both sides of the seam are the installed projects, never a stand-in.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

from pyssp_simulate import (
    SimulationSpec,
    prepare_runtime_ssp,
    read_result_csv,
)
from pyssp_standard import SSD, SSP, SSV
from pyssp_vv.evidence import (
    METRIC_COLUMNS,
    MetricRow,
    as_metric_view,
    read_metric_csv,
    write_metric_csv,
)
from pyssp_vv.judge import Verdict, judge
from pyssp_vv.policy import Criterion, Policy, Sufficiency
from sequence_extensions.flow import RunLog, RunOptions, execute_flow

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_ROOT = REPO_ROOT / "3rd_party" / "pyssp_workflow"
SYSML2_ROOT = WORKFLOW_ROOT / "3rd_party" / "pyssp_sysml2"
GOLDEN_TEST = SYSML2_ROOT / "tests" / "test_golden_artifacts.py"

#: The schema reviewed as EVAL-005. Copied literally, not imported, so a
#: rename in the writer or the judge has to be approved here too.
DURABLE_COLUMNS = (
    "signal",
    "max_abs_error",
    "max_shift_abs_error",
    "mean_abs_error",
    "rmse",
    "run_a_label",
    "run_a_min",
    "run_a_max",
    "run_b_label",
    "run_b_min",
    "run_b_max",
    "coverage",
    "shift_samples",
    "normalisation",
    "denominator",
    "normalised_max_abs_error",
    "undefined",
)


# --------------------------------------------------------------------------- #
# Seam 1: pyssp_standard -> pyssp_simulate
# --------------------------------------------------------------------------- #
SSD_NAME = "FacadeSSP"
SYSTEM_NAME = "plant"
COMPONENT_CONNECTORS = {
    "src": ("y",),
    "gain": ("u", "y"),
}


def _build_facade_ssp(path: Path) -> Path:
    """Write an SSP through the documented ``pyssp_standard`` facade."""
    with SSP(path, mode="w") as ssp:
        with ssp.system_structure() as ssd:
            ssd.rename(SSD_NAME)
            system = ssd.new_system(SYSTEM_NAME)
            system.add_connector("y", "output", "Real")

            source = system.add_component(
                "src",
                source="resources/src.fmu",
                component_type="application/x-fmu-sharedlibrary",
                implementation="CoSimulation",
            )
            source.add_connector("y", "output", "Real")

            gain = system.add_component(
                "gain",
                source="resources/gain.fmu",
                component_type="application/x-fmu-sharedlibrary",
                implementation="CoSimulation",
            )
            gain.add_connector("u", "input", "Real")
            gain.add_connector("y", "output", "Real")

            system.add_connection(
                start_element="src",
                start_connector="y",
                end_element="gain",
                end_connector="u",
            )
            system.add_connection(
                start_element="gain",
                start_connector="y",
                end_connector="y",
            )
    return path


def _ssd_shape(ssd_path: Path) -> dict[str, object]:
    with SSD(ssd_path, mode="r") as ssd:
        system = ssd.system
        assert system is not None
        return {
            "document": ssd.xml.name,
            "system": system.name,
            "components": {element.name: tuple(c.name for c in element.connectors)
                           for element in system.elements},
            "connectors": tuple(connector.name for connector in system.connectors),
        }


def test_standard_facade_output_survives_simulate_runtime_preparation(tmp_path: Path) -> None:
    """SSD facade method renamed/reshaped -> simulate fixtures stop building.

    Builds the SSP with ``SSD.new_system`` / ``add_component`` / ``add_connector``
    / ``add_connection``, then hands it to ``prepare_runtime_ssp``. Asserts the
    runtime copy keeps every name, and that the signal-resolution path the
    ``SimulationSpec`` feeds still maps engine columns to the declared
    ``<component>.<connector>`` names.
    """
    archive = _build_facade_ssp(tmp_path / "facade.ssp")
    assert zipfile.is_zipfile(archive)

    with prepare_runtime_ssp(archive) as runtime:
        assert runtime.ssd_name == "SystemStructure.ssd"
        assert runtime.container_names == (SSD_NAME, SYSTEM_NAME)
        assert (runtime.root / runtime.ssd_name).is_file()

        with zipfile.ZipFile(runtime.archive) as package:
            assert runtime.ssd_name in package.namelist()

        runtime_shape = _ssd_shape(runtime.root / runtime.ssd_name)
        assert runtime_shape["document"] == SSD_NAME
        assert runtime_shape["system"] == SYSTEM_NAME
        assert runtime_shape["components"] == {
            name: connectors for name, connectors in COMPONENT_CONNECTORS.items()
        }
        assert runtime_shape["connectors"] == ("y",)

        spec = SimulationSpec(ssp=runtime.archive)
        assert spec.ssp == runtime.archive
        assert spec.effective_step_size() == pytest.approx(0.01)

        # Engine-style columns, prefixed exactly as the runtime reports them.
        engine_csv = tmp_path / "engine.csv"
        rows = [
            ("time", ("0.0", "1.0")),
            (f"{SSD_NAME}.{SYSTEM_NAME}.src.y", ("1.0", "1.0")),
            (f"{SSD_NAME}.{SYSTEM_NAME}.gain.y", ("0.0", "1.0")),
        ]
        engine_csv.write_text(
            ",".join(name for name, _ in rows) + "\n"
            + "\n".join(
                ",".join(values[index] for _, values in rows) for index in range(2)
            )
            + "\n",
            encoding="utf-8",
        )

        result = read_result_csv(engine_csv, runtime.container_names)
        assert result.dtype.names == ("time", "gain.y", "src.y")


# --------------------------------------------------------------------------- #
# Seam 2: pyssp_vv evidence -> judge (and the workflow compare path)
# --------------------------------------------------------------------------- #
def _metric_row(
    signal: str,
    max_abs_error: float,
    *,
    coverage: float = 1.0,
    undefined: tuple[str, ...] = (),
) -> MetricRow:
    return MetricRow(
        signal=signal,
        max_abs_error=max_abs_error,
        max_shift_abs_error=0.0,
        mean_abs_error=max_abs_error / 4.0,
        rmse=max_abs_error / 2.0,
        run_a_label="reference",
        run_a_min=-1.0,
        run_a_max=1.0,
        run_b_label="candidate",
        run_b_min=-1.0,
        run_b_max=1.0,
        coverage=coverage,
        shift_samples=0,
        normalisation="reference_peak",
        denominator=1.0,
        normalised_max_abs_error=max_abs_error,
        undefined=undefined,
    )


def test_evidence_rows_round_trip_into_a_judge_verdict(tmp_path: Path) -> None:
    """Durable metric column renamed -> judge reads a table it cannot judge.

    Writes one CSV through the public evidence writer, reads it back, converts
    with ``as_metric_view`` and judges it. Expectations are computed by hand
    from the policy arithmetic (``limit = atol + rtol * reference_peak``), not
    read back out of ``judge``.
    """
    atol, rtol = 0.5, 0.0
    reference_peak = 1.0
    limit = atol + rtol * abs(reference_peak)

    passing = _metric_row("gain.y", 0.4)
    failing = _metric_row("gain.u", 0.75)
    unjudgeable = _metric_row("src.y", 0.1, coverage=0.5)

    path = write_metric_csv(tmp_path / "metrics.csv", [passing, failing, unjudgeable])

    assert METRIC_COLUMNS == DURABLE_COLUMNS
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert header == ",".join(DURABLE_COLUMNS)

    read_back = read_metric_csv(path)
    assert read_back == (passing, failing, unjudgeable)

    policy = Policy(
        criterion=Criterion(atol=atol, rtol=rtol),
        sufficiency=Sufficiency(min_coverage=0.9),
    )

    expected = {
        "gain.y": "pass" if 0.4 <= limit else "fail",
        "gain.u": "pass" if 0.75 <= limit else "fail",
        "src.y": "invalid",  # 0.5 coverage < 0.9: not legal to judge
    }
    assert expected == {"gain.y": "pass", "gain.u": "fail", "src.y": "invalid"}

    verdicts = {
        row.signal: judge([as_metric_view(row)], policy).verdict.value
        for row in read_back
    }
    assert verdicts == expected

    # Pessimistic aggregation, computed by hand: invalid dominates, then fail.
    combined = judge([as_metric_view(row) for row in read_back], policy)
    assert combined.verdict is Verdict.INVALID

    # The workflow comparison path must emit the same durable table.
    from pyssp_workflow import compare as workflow_compare

    assert workflow_compare.write_metric_csv is write_metric_csv


# --------------------------------------------------------------------------- #
# Seam 3: pyssp_sysml2 generated artifacts -> pyssp_standard readers
# --------------------------------------------------------------------------- #
def _golden_test_module() -> ModuleType:
    """Load the generator's own golden test for its pinned paths and cases."""
    spec = importlib.util.spec_from_file_location(
        "_pyssp_sysml2_golden_test", GOLDEN_TEST
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sysml2_goldens_are_readable_and_stable_under_pyssp_standard() -> None:
    """Writer renames a golden/case or reader re-serializes -> bytes differ.

    Reads the committed SSD and SSV artifacts the generator's golden test pins,
    validates them through ``SSD``/``SSV``, resolves every external parameter
    reference and mapping target inside the golden tree, and asserts the
    read-only open leaves every artifact byte-identical. No regeneration.
    """
    golden = _golden_test_module()
    golden_root: Path = golden.GOLDEN_ROOT
    cases: dict[str, str] = golden.CASES

    assert golden_root == GOLDEN_TEST.parent / "golden"
    assert {path.name for path in golden_root.iterdir() if path.is_dir()} == set(cases)

    for case, composition in cases.items():
        case_dir = golden_root / case
        ssd_path = case_dir / "SystemStructure.ssd"
        assert ssd_path.is_file(), f"missing golden SSD: {ssd_path}"

        ssd_bytes = ssd_path.read_bytes()
        with SSD(ssd_path, mode="r") as ssd:
            assert ssd.check_compliance() is True

            system = ssd.system
            assert system is not None
            # The composition the generator's golden test passes to generate_ssd.
            assert ssd.xml.name == composition
            assert system.name == composition

            connectors = {
                (element.name, connector.name)
                for element in system.elements
                for connector in element.connectors
            }
            bindings = system.get_parameter_bindings()
            assert bindings, f"{case}: SSD declares no parameter binding"

            for binding in bindings:
                assert binding.source is not None
                ssv_path = case_dir / binding.source
                assert ssv_path.is_file(), f"unresolved binding source: {ssv_path}"

                ssv_bytes = ssv_path.read_bytes()
                with SSV(ssv_path, mode="r") as ssv:
                    assert ssv.check_compliance() is True
                    assert ssv.xml.name == ssv_path.stem
                    parameter_names = [entry.name for entry in ssv.xml.parameters]
                assert ssv_path.read_bytes() == ssv_bytes
                assert parameter_names

                mapping = binding.parameter_mapping
                if mapping is not None and mapping.mapping is not None:
                    for entry in mapping.mapping.mappings:
                        component, _, connector = entry.target.partition(".")
                        assert (component, connector) in connectors, (
                            f"{case}: mapping target {entry.target!r} names no "
                            "component connector"
                        )

                if binding.prefix:
                    component = binding.prefix.rstrip(".")
                    assert component in {
                        element.name for element in system.elements
                    }, f"{case}: binding prefix {binding.prefix!r} names no component"
                    for name in parameter_names:
                        assert (component, name) in connectors, (
                            f"{case}: {component}.{name} is not a declared connector"
                        )

        assert ssd_path.read_bytes() == ssd_bytes


# --------------------------------------------------------------------------- #
# Seam 4: pyssp_workflow nodes -> sequence_extensions flow
# --------------------------------------------------------------------------- #
def test_workflow_node_runs_through_flow_and_is_logged(tmp_path: Path) -> None:
    """Node decorator protocol drifts -> workflow nodes stop being schedulable.

    Runs ``pyssp_workflow.nodes.write_bundle`` as a real flow run and asserts
    the audit log records it under its public ``.name`` with status ``ok``.
    """
    import pyssp_workflow.nodes as workflow_nodes
    from pyssp_vv.evidence import EvidenceBundle

    bundle = EvidenceBundle(
        assessment_id="contract-probe",
        inputs=(),
        verdicts=(),
        environment={"project": "ssp_references"},
    )
    out_dir = tmp_path / "evidence"

    run = execute_flow(
        workflow_nodes.write_bundle,
        bundle,
        str(out_dir),
        options=RunOptions(log=tmp_path / "logs", max_workers=1),
    )

    assert run.status == "ok"
    assert run.log is not None and Path(run.log).is_file()
    assert (out_dir / "evidence.json").is_file()
    assert EvidenceBundle.read(out_dir / "evidence.json").assessment_id == "contract-probe"

    records = RunLog.records(run.log)
    entries = RunLog.filter(
        records, record="node", node=workflow_nodes.write_bundle.name
    )
    assert len(entries) == 1
    assert entries[0]["status"] == "ok"
    assert entries[0]["path"] == [workflow_nodes.write_bundle.name]

    summary = RunLog.summarize(records)
    assert summary["status"] == "ok"
    assert summary["nodes"] == [
        {
            "node": workflow_nodes.write_bundle.name,
            "path": [workflow_nodes.write_bundle.name],
            "attempts": 1,
            "statuses": ["ok"],
            "duration_ms": summary["nodes"][0]["duration_ms"],
            "status": "ok",
        }
    ]


_ABSENT_FLOW_PROBE = """
import importlib.abc
import sys

TARGET = "sequence_extensions.flow"


class Blocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == TARGET:
            raise ModuleNotFoundError(f"No module named {fullname!r}", name=fullname)
        return None


sys.meta_path.insert(0, Blocker())
try:
    import pyssp_workflow.nodes  # noqa: F401
except ImportError as exc:
    print(f"RAISED {exc}")
else:
    print("IMPORTED")
"""

_BROKEN_FLOW_PROBE = """
import importlib.abc
import importlib.machinery
import sys

TARGET = "sequence_extensions.flow"


class BrokenLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ImportError("boom from inside flow")


class Broken(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == TARGET:
            return importlib.machinery.ModuleSpec(fullname, BrokenLoader(), is_package=True)
        return None


sys.meta_path.insert(0, Broken())
try:
    import pyssp_workflow.nodes  # noqa: F401
except ImportError as exc:
    print(f"RAISED {exc}")
else:
    print("IMPORTED")
"""


def _run_probe(code: str) -> str:
    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def test_nodes_import_requires_the_flow_subpackage() -> None:
    """Nodes guard removed or widened -> a missing extra fails without a hint.

    With ``sequence_extensions.flow`` shadowed out, importing
    ``pyssp_workflow.nodes`` must fail with the actionable extra hint, in a
    fresh interpreter (no uninstall).
    """
    line = _run_probe(_ABSENT_FLOW_PROBE)
    assert line.startswith("RAISED "), line
    assert "requires the 'flow' extra" in line


def test_nodes_import_does_not_mask_an_error_inside_flow() -> None:
    """Guard swallowing inner ImportErrors -> a broken install looks missing.

    With a shadowing ``flow`` whose body raises, the original error must reach
    the caller and must not be replaced by the missing-extra hint.
    """
    line = _run_probe(_BROKEN_FLOW_PROBE)
    assert line.startswith("RAISED "), line
    assert "boom from inside flow" in line
    assert "requires the 'flow' extra" not in line
