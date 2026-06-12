from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from scipy.io import savemat

from workflow.layout import ArtifactLayout
from workflow.setup import SimulationSetup, SimulationWindow
from workflow.simulate import (
    _fmpy_get_connections,
    _ssp4sim_config_payload,
    simulate_backend,
)
from utils.csv import unpack_mat_to_csv

try:
    from fmpy.ssp.ssd import System  # noqa: F401
    _HAVE_FMPY = True
except ImportError:
    _HAVE_FMPY = False


class MockConnector:
    def __init__(self, name: str, kind: str, path: str) -> None:
        self.name = name
        self.kind = kind
        self._path = path

    def __repr__(self) -> str:
        return f"MockConnector({self.name})"


class MockConnection:
    def __init__(self, startElement: str | None, startConnector: str,
                 endElement: str | None, endConnector: str) -> None:
        self.startElement = startElement
        self.startConnector = startConnector
        self.endElement = endElement
        self.endConnector = endConnector


class MockSystem:
    def __init__(self, name: str, connectors: list, connections: list,
                 elements: list | None = None) -> None:
        self.name = name
        self.connectors = connectors
        self.connections = connections
        self.elements = elements or []
        self._path = name


@pytest.fixture(autouse=True)
def isolated_repo_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr("workflow.layout.REPO_ROOT", repo_root)
    monkeypatch.setattr("workflow.simulate.REPO_ROOT", repo_root)
    monkeypatch.setattr("utils.config.REPO_ROOT", repo_root)


def test_ssp4sim_config_payload(tmp_path: Path) -> None:
    """R-003: Verify _ssp4sim_config_payload produces expected config dict structure.

    Backward trace: IMP-015 contract R-003.
    """
    ssp_root = tmp_path / "ssp_root"
    ssp_root.mkdir(parents=True)
    layout = ArtifactLayout(model_name="TestModel", case_name="testcase", ssp_root=ssp_root)
    window = SimulationWindow(start_time=0.0, stop_time=10.0, interval=0.1)
    setup = SimulationSetup(
        layout=layout,
        window=window,
        tolerance=1e-5,
        backends=("ssp4sim",),
        compare_signals=("signal",),
        root_system_name="system",
    )
    result_file = tmp_path / "result.csv"
    log_file = tmp_path / "sim.log"

    config = _ssp4sim_config_payload(
        setup=setup,
        ssp_root=ssp_root,
        result_file=result_file,
        log_file=log_file,
    )

    # 15 sub-checks
    assert "simulation" in config
    sim = config["simulation"]
    assert isinstance(sim, dict)

    assert sim["ssp"] == str(ssp_root.resolve())
    assert sim["ssd"] == "SystemStructure.ssd"

    assert sim["start_time"] == pytest.approx(0.0)
    assert sim["stop_time"] == pytest.approx(10.0)
    assert sim["timestep"] == pytest.approx(0.1)
    assert sim["tolerance"] == pytest.approx(1e-5)
    assert sim["realtime"] is False
    assert sim["working_dir"] == str(result_file.parent.resolve())

    executor = sim["executor"]
    assert isinstance(executor, dict)
    for key in ("method", "thread_pool_workers", "forward_derivatives", "sub_step", "jacobi", "seidel"):
        assert key in executor

    recording = sim["recording"]
    assert recording["enable"] is True
    assert recording["result_file"] == str(result_file.resolve())

    csv_cfg = recording["csv"]
    assert csv_cfg["enable"] is True
    assert csv_cfg["file"] == str(result_file.resolve())
    assert csv_cfg["interval"] == pytest.approx(0.1)

    influx_cfg = recording["influx"]
    assert influx_cfg["enable"] is False

    log_cfg = sim["log"]
    assert log_cfg["file"] == str(log_file.resolve())
    assert log_cfg["level_terminal"] == "error"


@pytest.mark.skipif(not _HAVE_FMPY, reason="fmpy not installed")
def test_fmpy_connections_empty(tmp_path: Path) -> None:
    """R-004: Empty system returns empty connection list.

    Backward trace: IMP-015 contract R-004.
    """
    root = MockSystem("system", connectors=[], connections=[], elements=[])
    with (
        patch("fmpy.ssp.ssd.build_path", side_effect=lambda obj: obj._path),
        patch("fmpy.ssp.ssd.find_connectors", return_value=[]),
    ):
        result = _fmpy_get_connections(root)
    assert result == []


@pytest.mark.skipif(not _HAVE_FMPY, reason="fmpy not installed")
def test_fmpy_connections_orphan_raises_keyerror(tmp_path: Path) -> None:
    """R-004: Orphan output connector raises KeyError.

    Backward trace: IMP-015 contract R-004.
    """
    out_con = MockConnector("out", "output", "system.out")
    root = MockSystem("system", connectors=[out_con], connections=[], elements=[])
    with (
        patch("fmpy.ssp.ssd.build_path", side_effect=lambda obj: obj._path),
        patch("fmpy.ssp.ssd.find_connectors", return_value=[out_con]),
    ):
        with pytest.raises(KeyError, match="Missing connection"):
            _fmpy_get_connections(root)


@pytest.mark.skipif(not _HAVE_FMPY, reason="fmpy not installed")
def test_fmpy_connections_root_to_child(tmp_path: Path) -> None:
    """R-004: Root output connected to child input returns connection pair(s).

    The traversal records the connection once when processing the root
    output connector and once when processing the child input connector,
    so the result list contains two identical pairs for this topology.

    Backward trace: IMP-015 contract R-004.
    """
    out_con = MockConnector("out", "output", "system.out")
    in_con = MockConnector("in", "input", "system.child.in")
    child = MockSystem("child", connectors=[in_con], connections=[], elements=[])
    child._path = "system.child"
    conn = MockConnection(startElement=None, startConnector="out",
                          endElement="child", endConnector="in")
    root = MockSystem("system", connectors=[out_con], connections=[conn], elements=[child])

    all_connectors = [out_con, in_con]
    with (
        patch("fmpy.ssp.ssd.build_path", side_effect=lambda obj: obj._path),
        patch("fmpy.ssp.ssd.find_connectors", return_value=all_connectors),
    ):
        result = _fmpy_get_connections(root)

    # The function records the connection twice: once from the root output
    # processing loop, once from the child input processing loop.
    assert len(result) == 2
    for start_con, end_con in result:
        assert start_con.name == "out"
        assert end_con.name == "in"


def _uint16_char_matrix(strs: list[str]) -> np.ndarray:
    """Build a Dymola-style character matrix as uint16 (MATLAB native char type).

    The returned array has shape (max_str_len, num_strings) so that
    column *j* holds the character codes for the *j*-th string.
    """
    max_len = max(len(s) for s in strs)
    return np.array(
        [[ord(c) for c in s.ljust(max_len)] for s in strs],
        dtype=np.uint16,
    ).T


@pytest.fixture
def _patch_decode_char_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch decode_char_matrix to accept uint16 character matrices.

    ``savemat`` cannot correctly round-trip NumPy ``U1`` character arrays
    through a MAT file (it adds an extra dimension and scrambles element
    order).  Dymola stores character data as ``uint16`` matrices, which
    ``savemat`` preserves faithfully.  This patch lets ``decode_char_matrix``
    process those uint16 matrices by converting them to ``U1`` first.
    """
    import utils.csv as csv_mod

    original = csv_mod.decode_char_matrix

    def _patched(value: np.ndarray) -> list[str]:
        if value.dtype == np.uint16:
            as_u1 = np.array(
                [[chr(int(value[i, j])) for j in range(value.shape[1])]
                 for i in range(value.shape[0])],
                dtype="U1",
            )
            return original(as_u1)
        return original(value)

    monkeypatch.setattr(csv_mod, "decode_char_matrix", _patched)


def test_unpack_mat_to_csv(tmp_path: Path, _patch_decode_char_matrix: None) -> None:
    """R-005: Synthetic MAT file produces expected CSV output.

    Backward trace: IMP-015 contract R-005.
    """
    # Build Dymola-style synthetic MAT using uint16 for char arrays
    # (MATLAB stores characters as uint16 matrices)
    data_1 = np.empty((0, 0), dtype=np.float64)
    data_2 = np.array([
        [0.0, 1.0, 2.0],
        [10.0, 20.0, 30.0],
    ], dtype=np.float64)
    data_info = np.array([
        [0, 2],
        [1, 2],
    ], dtype=np.int64)

    # Character matrices: shape (max_str_len, num_strings) as uint16
    names = _uint16_char_matrix(["time", "signal"])
    descriptions = _uint16_char_matrix(["Independent time axis", "Test signal"])
    Aclass = _uint16_char_matrix(["Trajectory"])

    mat_path = tmp_path / "test.mat"
    savemat(mat_path, {
        "Aclass": Aclass,
        "name": names,
        "description": descriptions,
        "dataInfo": data_info,
        "data_1": data_1,
        "data_2": data_2,
    })

    output_path = unpack_mat_to_csv(mat_path)

    assert output_path.exists()
    assert output_path.suffix == ".csv"

    # Read CSV and verify
    import csv
    with open(output_path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    assert rows[0] == ["time", "signal"]

    time_vals = [float(r[0]) for r in rows[1:]]
    signal_vals = [float(r[1]) for r in rows[1:]]
    assert time_vals == pytest.approx([0.0, 1.0, 2.0])
    assert signal_vals == pytest.approx([10.0, 20.0, 30.0])


def test_unpack_mat_to_csv_raises_on_missing_file(tmp_path: Path) -> None:
    """R-006: Missing MAT file raises FileNotFoundError.

    Backward trace: IMP-015 contract R-006.
    """
    missing = tmp_path / "nonexistent.mat"
    with pytest.raises(FileNotFoundError, match="MAT file not found"):
        unpack_mat_to_csv(missing)


@pytest.mark.parametrize(
    ("backend", "expected_adapter_name"),
    [
        ("ssp4sim", "simulate_ssp4sim"),
        ("omsimulator", "simulate_omsimulator"),
        ("fmpy", "simulate_fmpy"),
        ("SSP4SIM", "simulate_ssp4sim"),
    ],
)
def test_simulate_backend_dispatch_routes(backend: str, expected_adapter_name: str) -> None:
    """R-007: simulate_backend routes to correct adapter per backend string.

    Backward trace: IMP-015 contract R-007.
    """
    class _MockRequest:
        def __init__(self, backend: str) -> None:
            self.backend = backend

    request = _MockRequest(backend)
    adapter_path = f"workflow.simulate.{expected_adapter_name}"
    with patch(adapter_path) as mock_adapter:
        mock_adapter.return_value = None
        simulate_backend(request)
    mock_adapter.assert_called_once_with(request)


def test_simulate_backend_unknown_raises() -> None:
    """R-007: Unknown backend raises NotImplementedError.

    Backward trace: IMP-015 contract R-007.
    """
    class _MockRequest:
        def __init__(self, backend: str) -> None:
            self.backend = backend

    request = _MockRequest("nonexistent")
    with pytest.raises(NotImplementedError, match="nonexistent"):
        simulate_backend(request)
