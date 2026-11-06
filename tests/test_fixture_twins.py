"""Fixture twins: the canonical set against the pinned copy (historically).

The pinned ``pyssp_sysml2/3rd_party/experimental_pyssp_standard`` checkout kept
a ``pytest/__fixture__`` copy of the same EMBRACE example, ~5.8 MB duplicated
on disk. That copy was part of the vendored ``3rd_party/pyssp_workflow``
submodule tree, which the flat-ecosystem migration removed; the nested pinned
tree no longer exists in the flat workspace, so there is nothing to compare.

This module skips wholesale. If a pinned counterpart is ever reintroduced (for
example as a fixture set inside ``repos/pyssp_sysml2``), point ``PINNED`` at it
and re-enable the twin tests below.
"""

from __future__ import annotations

import pytest

pytest.skip(
    "flat ecosystem migration removed the vendored pinned fixture copy; a "
    "canonical fixture set lives in repos/experimental_pyssp_standard/tests/"
    "fixtures but its pinned twin no longer exists",
    allow_module_level=True,
)