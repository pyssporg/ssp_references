/* Example 05 -- several variation points in one architecture.
 *
 * Pattern: one composition carries three variation points at the same time.
 * "source" selects the signal source, "gain" selects the gain topology, and
 * "scenario" on the study selects a parameter set. Each point is declared the
 * same way examples 01 and 02 declare theirs: a variation definition whose
 * variant members name the alternatives. Nothing else in the file is new.
 * Standard anchor: SysML v2 section 7.6.7 (Variations and Variants; metamodel
 * VariantMembership); the Variability note in section 7.6.1 states
 * that selecting a variant often affects other design choices.
 * Vocabulary: ISO/IEC 26550:2015 3.29 (variation point) and 3.28 (variant).
 * 26580:2021 3.20 and 3.19 are the feature-based specialisations of the same
 * two terms; this file uses the general 26550 phrasing because the points are
 * asset variation points, not features of a feature catalogue.
 *
 * Combinatorial space: the three points are independent, so the architecture
 * spans 2 x 2 x 3 = 12 selections. Source has two alternatives (step, sine),
 * gain has two (single stage, two stages in series), and scenario has three
 * (baseline, late step, high gain). No constraint couples the points here; the
 * 12 combinations are all legal by construction. Example 06 adds constraints
 * that remove most of them.
 *
 * Expected SSP/FMI mapping: one selection yields one SSP. The chosen source
 * variant contributes one <Part> typed by its FMU; the chosen gain variant
 * contributes either one <Part> (single stage) or two <Part> entries joined by
 * an internal connector (cascaded), so the SSD is not just differently typed
 * between the two gain selections, it has a different element count. The
 * chosen scenario contributes one <name>.ssv parameter set, and the SSD stays
 * identical across scenario selections. Selection identity has to be recorded
 * outside the artifact, because SSP has no variant field.
 *
 * Note on the parameter binding: only the gain parameter port is bound in the
 * study. The source variants expose different parameter ports (StepParameters
 * against SineParameters), so no single binding resolves before a source
 * variant is chosen. That is a real limitation of the current dialect, not a
 * simplification of the example.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors. The
 * parsed model carries no variation marker -- the variation definitions arrive
 * as ordinary part definitions, with no variation flag and no variant members
 * at all -- but the frame around them is the one examples 01-04 already use.
 * Generation succeeds and flattens all three points in one step: the SSD holds
 * two components, "source" and "gain", both with an empty source attribute, the
 * signal and parameter connectors those variation definitions declare, and the
 * single connection source.y to gain.u. Nothing selection-related reaches the
 * artifact, so no selection can change it: step and sine, one stage and two,
 * baseline and high gain all produce this same SSD.
 */
package MultipleVariationPoints {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def SineParameters :> ParameterInterface {
    attribute amplitude : Real;
    attribute f : Real;
    attribute offset : Real;
    attribute phase : Real;
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

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def SignalSource {
    out port y : RealSignal;
  }

  part def Step :> SignalSource {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port :>> y : RealSignal;
  }

  part def Sine :> SignalSource {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port :>> y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
  }

  part def CascadedGain {
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
    part firstStage : Gain;
    part secondStage : Gain;
    connect u to firstStage.u;
    connect firstStage.y to secondStage.u;
    connect secondStage.y to y;
    connect parameters to firstStage.parameters;
    connect parameters to secondStage.parameters;
  }

  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation part def GainChoice {
    in port u : RealSignal;
    out port y : RealSignal;
    in port parameters : GainParameters;
    variant part singleStage : Gain;
    variant part twoStages : CascadedGain;
  }

  variation attribute def ScenarioChoice {
    variant attribute baseline : BaselineScenario;
    variant attribute lateStep : LateStepScenario;
    variant attribute highGain : HighGainScenario;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : GainChoice;
    connect source.y to gain.u;
  }

  part def test_selected :> Study {
    doc /* One study per selection; the selection itself is not recorded here. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioChoice;
    part sut : System;

    bind sut.gain.parameters.k = scenario.k;
  }
}
