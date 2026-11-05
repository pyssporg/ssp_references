"""Transitional contract for the pyssp_sysml2 v0.4.0 re-export shims.

The SysML dialect moved to ``pycps_sysml2``; v0.4.0 keeps re-export shims so
external users survive the move, and v0.5.0 deletes them. While they exist the
shims must expose the canonical objects unchanged, otherwise a consumer could
silently keep importing a stale copy. Delete this file with the shims.
"""

from __future__ import annotations

import pyssp_sysml2.metadata.roles as legacy_roles
import pyssp_sysml2.model as legacy_model
import pyssp_sysml2.parameters.selection as legacy_selection

from pycps_sysml2.metadata.roles import model_usage
from pycps_sysml2.model import load
from pycps_sysml2.parameters.selection import analysis_plans


def test_model_load_is_the_canonical_function() -> None:
    """``pyssp_sysml2.model.load`` re-exports the pycps_sysml2 function."""
    assert legacy_model.load is load


def test_analysis_plans_is_the_canonical_function() -> None:
    """The shim cannot drift into a wrapper with a different signature."""
    assert legacy_selection.analysis_plans is analysis_plans
    assert analysis_plans.__module__ == "pycps_sysml2.parameters.selection"


def test_model_usage_is_the_canonical_function() -> None:
    """Role inspection keeps resolving through the shim until v0.5.0."""
    assert legacy_roles.model_usage is model_usage
    assert model_usage.__module__ == "pycps_sysml2.metadata.roles"
