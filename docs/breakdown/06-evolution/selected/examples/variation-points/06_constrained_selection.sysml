/* Example 06 -- constrained selection: legality rules over several points.
 *
 * Pattern: the architecture of example 05, unchanged, plus two constraints
 * that remove legal-by-construction combinations. "Selecting the sine source
 * requires the single-stage gain" is a requirement from one variant on
 * another; "selecting the sine source excludes the high-gain scenario" is an
 * exclusion from one variant on a variant of a different point. Both are
 * ordinary SysML constraint definitions with an assertion on the composition
 * or on the study, not a new keyword: SysML v2 section 7.6.1 says constraints
 * "can be used to constrain the available choices for a given variant" and the
 * specification's own variability example (Annex A.12) draws exactly this as a
 * named "assert constraint" over operator expressions.
 * Standard anchor: section 7.20.2 (Constraint Definitions and Usages) and 7.20.3
 * (Assert Constraint Usages); variation and variants as in example 05 (7.6.7).
 *
 * Vocabulary, ISO/IEC 26550:2015:
 * - 3.24 variability constraint: "constraint relationships between a variant
 *   and a variation point, between two variants, and between two variation
 *   points". Both rules below are variant-to-variant constraints, so both are
 *   variability constraints in the 3.24 sense: sine-requires-single-stage and
 *   sine-excludes-high-gain.
 * - 3.25 variability dependency: "relationship between a variation point and a
 *   set of variants, which indicates that the variation point implies a
 *   decision about the variants", with a mandatory and an optional kind. The
 *   three points in this file are all mandatory: each must resolve to exactly
 *   one variant. That obligation, not the two rules, is what makes an
 *   unresolved selection illegal.
 * So the mapping is: both operator rules are 3.24; the one-of obligation per
 * point is a 3.25 mandatory variability dependency. 26580:2021 3.6 feature
 * constraint is the feature-catalogue specialisation of 3.24 and does not
 * apply here, because these are asset variation points, not features.
 *
 * Effect on the space: example 05 spans 2 x 2 x 3 = 12 selections. The
 * requirement removes the three sine-with-two-stages selections; the exclusion
 * removes sine-with-high-gain at single stage. Eight of twelve selections
 * remain legal.
 *
 * Expected SSP/FMI mapping: constraints change nothing in the artifact. A
 * build tool has to evaluate them before generation, because SSP, SSD, SSV and
 * SSM carry no place for a legality rule; the only observable difference
 * between a legal and an illegal selection is whether a package is produced.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors. The
 * constraint definitions, the named constraint usages with their parameter
 * bindings, and both "assert <name>" statements are retained by the parser as
 * constraint usages. The adapter does not read them: it walks part, port,
 * attribute and requirement definitions only, and its architecture model has no
 * constraint element, so no constraint reaches generation and none can be
 * evaluated. Generation of System therefore succeeds, and the SSD it writes is
 * byte-for-byte the one example 05 writes, whether or not the recorded
 * combination is legal.
 */
package ConstrainedSelection {
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

  constraint def SineRequiresSingleStage {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenGain == GainChoice::singleStage
  }

  constraint def SineExcludesHighGain {
    in chosenSource : SourceChoice;
    in chosenScenario : ScenarioChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenScenario != ScenarioChoice::highGain
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : GainChoice;
    connect source.y to gain.u;

    /* Reuse shape: name the constraint, bind its parameters, assert the name. */
    constraint requiresSingleStage : SineRequiresSingleStage {
      in chosenSource = source;
      in chosenGain = gain;
    }
    assert requiresSingleStage;
  }

  part def test_selected :> Study {
    doc /* One study per selection; the scenario point lives here. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioChoice;
    part sut : System;

    bind sut.gain.parameters.k = scenario.k;

    /* Same reuse shape across the composition boundary: the scenario point
     * lives on the study, so the exclusion has to be asserted here. */
    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = scenario;
    }
    assert excludesHighGain;
  }
}
