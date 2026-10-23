"""Shared build helper for SysML-authored fixtures.

Derives a study and its exported model SSP from ``architecture/*.sysml``, strips
model-exchange metadata from the unpacked FMUs, and packages the study scenario
into the exported SSP so the build output is a self-contained engine input.

The default ``package`` step adds the study SSV and SSM as one root parameter
binding. A fixture whose parameter-application form differs passes its own
``package`` callback; that is the fixture-specific residue.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from pyssp_standard import SSP, SSM, SSV, ParameterMappingReference, unpack_archive
from pyssp_workflow.authoring import derive_ssp_from_sysml, derive_study_from_sysml
from pyssp_workflow.execute import package_scenario
from pyssp_workflow.params import StudyDescriptor, read_study_descriptor

from utils.filesystem import reset_dir
from utils.fmu import strip_model_exchange

PackageStep = Callable[[Path, StudyDescriptor], None]
PopulateStep = Callable[[Path], None]


def _strip_model_exchange(model_root: Path) -> None:
    for description in sorted(model_root.rglob("modelDescription.xml")):
        strip_model_exchange(description.parent)


def build_study(
    architecture_dir: Path,
    study_dir: Path,
    composition: str,
    model_name: str,
) -> Path:
    reset_dir(study_dir)
    derive_study_from_sysml(
        architecture_dir,
        study_dir,
        composition,
        model_name=model_name,
    )
    return study_dir


def build_model(
    architecture_dir: Path,
    model_build_dir: Path,
    composition: str,
    repo_root: Path,
    *,
    allow_missing_fmus: bool = False,
    populate: PopulateStep | None = None,
) -> Path:
    """Export the model SSP and unpack it into *model_build_dir*.

    ``allow_missing_fmus`` exports a design structure whose FMUs are not built
    yet. ``populate`` receives the archive path between export and unpacking so
    a fixture can attach the missing FMUs before the artifact is written.
    """
    reset_dir(model_build_dir)
    with tempfile.TemporaryDirectory(prefix=f"{model_build_dir.name}_") as temp_dir:
        archive = Path(temp_dir) / "model.ssp"
        derive_ssp_from_sysml(
            architecture_dir,
            archive,
            composition,
            fmu_root=repo_root,
            allow_missing_fmus=allow_missing_fmus,
        )
        if populate is not None:
            populate(archive)
        unpack_archive(
            archive,
            model_build_dir,
            recursive_fmus=True,
            overwrite=True,
        )
    _strip_model_exchange(model_build_dir)
    return model_build_dir


def scenario_values(descriptor: StudyDescriptor) -> dict[str, float]:
    """The study scenario as ``{ssv member name: value}``."""
    with SSV(descriptor.ssv_path, mode="r") as ssv:
        return {
            parameter.name: float(parameter.attributes["value"])
            for parameter in ssv.xml.parameters
        }


def scenario_targets(descriptor: StudyDescriptor) -> dict[str, float]:
    """The study scenario keyed by the mapped SSP target name."""
    values = scenario_values(descriptor)
    with SSM(descriptor.ssm_path, mode="r") as ssm:
        mappings = [(mapping.source, mapping.target) for mapping in ssm.xml.mappings]
    return {target: values[source] for source, target in mappings}


def scenario_mappings(descriptor: StudyDescriptor) -> list[tuple[str, str]]:
    """The study ``(member name, target)`` mapping pairs."""
    with SSM(descriptor.ssm_path, mode="r") as ssm:
        return [(mapping.source, mapping.target) for mapping in ssm.xml.mappings]


def package_inline_root(model_build_dir: Path, descriptor: StudyDescriptor) -> None:
    """Apply the scenario as one inline root parameter set keyed by target name."""
    values = scenario_targets(descriptor)
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset(values, binding_name=descriptor.set_name)


def package_external_target_named(
    model_build_dir: Path, descriptor: StudyDescriptor
) -> None:
    """Apply the scenario as an external SSV whose names are the SSP targets.

    This is the no-mapping form: the parameter names are the hierarchical
    targets, so the binding needs no ``.ssm``.
    """
    values = scenario_targets(descriptor)
    with tempfile.TemporaryDirectory(prefix=f"{descriptor.set_name}_") as temp_dir:
        ssv_path = Path(temp_dir) / f"{descriptor.set_name}.ssv"
        with SSV(ssv_path, mode="w") as ssv:
            ssv.xml.name = descriptor.set_name
            for name, value in values.items():
                ssv.xml.add_parameter(parname=name, ptype="Real", value=value)
        with SSP(model_build_dir, mode="a") as ssp:
            ssp.add_external_parameterset(ssv_path)


def _resolve_system(root_system, path_parts: list[str]):
    system = root_system
    for name in path_parts:
        element = next(
            (candidate for candidate in system.elements if candidate.name == name),
            None,
        )
        if element is None:
            raise KeyError(f"No element '{name}' under '{system.name}'")
        system = element
    return system


def apply_inline_components(
    model_build_dir: Path,
    descriptor: StudyDescriptor,
    *,
    only: set[str] | None = None,
) -> None:
    """Apply the scenario as inline parameter sets on the mapped components.

    Each mapped target is ``<component path>.<parameter>``; the component path
    may cross nested systems. ``only`` limits application to the given
    component paths.
    """
    targets = scenario_targets(descriptor)
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            root = ssd.xml.system
            for target, value in targets.items():
                *component_path, parameter = target.split(".")
                component_name = ".".join(component_path)
                if only is not None and component_name not in only:
                    continue
                system = _resolve_system(root, component_path[:-1])
                component = next(
                    candidate
                    for candidate in system.elements
                    if candidate.name == component_path[-1]
                )
                component.extend_inline_parameterset({parameter: value})


def package_inline_with_mapping(
    model_build_dir: Path, descriptor: StudyDescriptor
) -> None:
    """Apply the scenario inline, with an external SSM resource for the mapping."""
    values = scenario_values(descriptor)
    mapping_name = descriptor.ssm_path.name
    with SSP(model_build_dir, mode="a") as ssp:
        with ssp.system_structure() as ssd:
            ssd.extend_system_parameterset(values, binding_name=descriptor.set_name)
            binding = next(
                candidate
                for candidate in ssd.xml.system.parameter_bindings
                if candidate.source is None and candidate.parameter_set is not None
            )
            binding.parameter_mapping = ParameterMappingReference(
                source=f"resources/{mapping_name}"
            )
        ssp.add_resource(descriptor.ssm_path)


def build_fixture(
    *,
    model_dir: Path,
    repo_root: Path,
    model_name: str,
    composition: str,
    study: str,
    build_name: str = "model",
    package: PackageStep | None = None,
    allow_missing_fmus: bool = False,
    populate: PopulateStep | None = None,
) -> Path:
    """Build the study, the exported model SSP, and the packaged runnable SSP."""
    architecture_dir = model_dir / "architecture"
    study_dir = repo_root / "artifacts" / "studies" / model_name / study
    model_build_dir = (
        repo_root / "artifacts" / "models" / model_name / study / build_name
    )

    build_study(architecture_dir, study_dir, study, model_name)
    build_model(
        architecture_dir,
        model_build_dir,
        composition,
        repo_root,
        allow_missing_fmus=allow_missing_fmus,
        populate=populate,
    )

    descriptor = read_study_descriptor(study_dir / "study.json")
    if package is None:
        package_scenario(model_build_dir, descriptor.ssv_path, descriptor.ssm_path)
    else:
        package(model_build_dir, descriptor)

    return model_build_dir
