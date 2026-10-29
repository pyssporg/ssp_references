/* Example 02 -- attribute variation: one structure, alternative parameter sets.
 *
 * Pattern: the composition does not change; the variation point selects among
 * alternative attribute definitions, each of which fixes a full parameter set
 * (the same attributes with different values). The Analysis binds the selected
 * set into the FMU parameter ports, so the choice is a value choice, not a
 * topology choice.
 * Standard anchor: SysML v2 section 7.6.7 (variation, variant; metamodel
 * VariantMembership).
 *
 * Expected SSP/FMI mapping: the selected variant's attribute def becomes one
 * <name>.ssv parameter set inside the SSP, with one <Parameter> per attribute;
 * SystemStructure.ssd is byte-identical for every selection, because neither
 * parts nor connectors move. SystemStructure.ssm maps each FMU value reference
 * to the attribute of the same name. FMI gains nothing: the FMUs are the same
 * binaries with the same value references in every variant.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors, but the
 * parsed model has no variation flag and no variant members. ScenarioChoice is
 * an empty attribute definition, the three candidate sets are collected like
 * any other attribute definition, and the "scenario" attribute of the Analysis is
 * typed by ScenarioChoice, which carries none of the bound attributes. A build
 * therefore cannot tell which set -- if any -- was selected.
 *
 * Note: the binds below are written against the resolved variant, so they
 * become well-formed only after a selection names one variant of
 * ScenarioChoice. Binding before selection is exactly the ambiguity the
 * implementer has to reject.
 */
package AttributeVariation {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def ParameterSet;

  attribute def BaselineScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 3.0;
  }

  attribute def LateStepScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.75;
    attribute k = 3.0;
  }

  attribute def HighGainScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 9.0;
  }

  variation attribute def ScenarioChoice {
    variant attribute baseline : BaselineScenario;
    variant attribute lateStep : LateStepScenario;
    variant attribute highGain : HighGainScenario;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
    attribute tolerance : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
    attribute tolerance = 0.0001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def StepFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Step/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Step {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port parameters : GainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }

  part def test_selected_scenario :> Analysis {
    doc /* Parameter variation over one fixed structure. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioChoice;
    part sut : System;

    bind sut.step.parameters.height = scenario.height;
    bind sut.step.parameters.offset = scenario.offset;
    bind sut.step.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }
}
