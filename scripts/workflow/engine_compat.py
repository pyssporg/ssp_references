"""Compatibility shims for engine gaps that ``pyssp_simulate`` does not cover.

Both workarounds are scoped to the runtime call path and document a concrete
upstream gap. Remove them once the corresponding fix lands in
``pyssp_simulate`` (or in the engine adapters it wraps).
"""

from __future__ import annotations

from contextlib import contextmanager


def fmpy_get_connections(system, connectors=None):
    """Resolve FMPy SSP connections for the generated runtime archive.

    FMPy's built-in resolver trips over some system-boundary connections in
    these fixtures, especially models like dcmotor that wire inputs/outputs
    through the root system. We mirror its traversal here and fix that branch
    so the runtime archive can be instantiated without changing the models.
    """
    from fmpy.ssp.ssd import System, build_path, find_connectors

    if connectors is None:
        connectors = {}
        for connector in find_connectors(system):
            connectors[build_path(connector)] = connector

    cons = []

    for connector in system.connectors:
        if connector.kind == "output":
            start_p = None
            end_p = None
            for connection in system.connections:
                if connection.endElement is None and connection.endConnector == connector.name:
                    start_p = build_path(system) + "." + connection.startElement + "." + connection.startConnector
                    end_p = build_path(connector)
                    break
                if connection.startElement is None and connection.startConnector == connector.name:
                    start_p = build_path(connector)
                    end_p = build_path(system) + "." + connection.endElement + "." + connection.endConnector
                    break
            if start_p is None or end_p is None:
                raise KeyError(f"Missing connection for connector {build_path(connector)}")
            cons.append((connectors[start_p], connectors[end_p]))

    for element in system.elements:
        for connector in element.connectors:
            if connector.kind == "input":
                end_p = build_path(element) + "." + connector.name
                start_p = None
                for connection in system.connections:
                    if connection.endElement == element.name and connection.endConnector == connector.name:
                        start_p = build_path(system)
                        if connection.startElement is not None:
                            start_p += "." + connection.startElement
                        start_p += "." + connection.startConnector
                        break
                    if connection.startElement == element.name and connection.startConnector == connector.name:
                        start_p = build_path(system)
                        if connection.endElement is not None:
                            start_p += "." + connection.endElement
                        start_p += "." + connection.endConnector
                        break
                if start_p is None:
                    raise KeyError(f"Missing connection for connector {build_path(element) + '.' + connector.name}")
                cons.append((connectors[start_p], connectors[end_p]))

    for element in system.elements:
        if isinstance(element, System):
            cons += fmpy_get_connections(element, connectors=connectors)

    return cons


@contextmanager
def patched_fmpy_ssp_runtime():
    """Temporarily relax FMPy's SSP loader for this repository's fixtures.

    The generated SSP archives are current enough for our other backends, but
    FMPy's loader still rejects some SSP 2.0 schema details. We therefore skip
    validation and swap in the local connection resolver above so boundary
    wiring continues to work for models that depend on it.

    Upstream gap: ``pyssp_simulate`` calls FMPy directly, so this shim must
    wrap the call around the whole simulate invocation.
    """
    from fmpy.ssp import simulation as fmpy_simulation
    from fmpy.ssp import ssd as fmpy_ssd

    original_validate_tree = fmpy_ssd.validate_tree
    original_get_connections = fmpy_simulation.get_connections

    def _no_validate(*args, **kwargs):
        return None

    # Keep the patch scoped to the FMPy runtime call path only.
    fmpy_ssd.validate_tree = _no_validate
    fmpy_simulation.get_connections = fmpy_get_connections
    try:
        yield
    finally:
        fmpy_ssd.validate_tree = original_validate_tree
        fmpy_simulation.get_connections = original_get_connections


def configure_omsimulator() -> None:
    """Apply the OMSimulator command-line options this fixture suite requires.

    ``pyssp_simulate`` only sets ``Settings.suppressPath``. These options keep
    parameter values in the result CSV and tolerate the fixtures' initial
    unknowns/input handling.

    Upstream gap: ``pyssp_simulate``'s OMSimulator backend does not expose
    these engine options.
    """
    from OMSimulator.capi import Capi, Status

    # The OMSimulator package already applies suppressPath while loading FMUs,
    # so only set the remaining historical options here.
    for option in (
        "--ignoreInitialUnknowns=true",
        "--wallTime=true",
        "--emitEvents=false",
        "--inputExtrapolation=true",
        "--addParametersToCSV=true",
    ):
        status = Capi.setCommandLineOption(option)
        if status != Status.ok:
            raise RuntimeError(f"Failed to set OMSimulator command line option {option!r}: {status}")
