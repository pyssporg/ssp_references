/* Example 04 -- no variation construct: N models are N compositions.
 *
 * Pattern: the alternative "N models = N compositions" route. Every
 * alternative is a sibling part definition specialising SspModel, with its own
 * analyses; nothing in the file marks a choice, so nothing can be flattened and
 * nothing needs selection. This is the layout the current build already
 * supports and the baseline the variation work is measured against.
 * Standard anchor: none. No element of SysML v2 section 7.6.7 appears here;
 * the file exists to show what the repository does instead.
 *
 * Expected SSP/FMI mapping: one SSP per composition, each with one
 * SystemStructure.ssd and one registry case named after the composition (here
 * step_gain_baseline, sine_gain_baseline, step_gain_high). Selection is
 * expressed by naming a different composition on the command line, so no
 * selection identity travels inside the architecture and the authored source
 * is duplicated rather than shared.
 *
 * Pinned toolchain (sysmlpy 0.96.4): this file parses with no errors and loses
 * nothing, because it uses only constructs the adapter already reads. It is
 * the control for examples 01-03: any loss observed there is attributable to
 * the variation construct, not to the surrounding dialect.
 */
package MultiCompositionModels {
  part def SspModel;
  part def Analysis;

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

  attribute def HighGainScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 9.0;
  }

  attribute def SineScenario :> ParameterSet {
    attribute amplitude = 1.0;
    attribute f = 1.0;
    attribute k = 3.0;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
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

  part def Step {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port y : RealSignal;
  }

  part def Sine {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port parameters : GainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def step_gain_baseline :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }

  part def sine_gain_baseline :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part sine : Sine;
    part gain : Gain;
    connect sine.y to gain.u;
  }

  part def step_gain_high :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step : Step;
    part gain : Gain;
    connect step.y to gain.u;
  }

  part def test_step_gain_baseline :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : BaselineScenario;
    part sut : step_gain_baseline;

    bind sut.step.parameters.height = scenario.height;
    bind sut.step.parameters.offset = scenario.offset;
    bind sut.step.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def test_sine_gain_baseline :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : SineScenario;
    part sut : sine_gain_baseline;

    bind sut.sine.parameters.amplitude = scenario.amplitude;
    bind sut.sine.parameters.f = scenario.f;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def test_step_gain_high :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : HighGainScenario;
    part sut : step_gain_high;

    bind sut.step.parameters.height = scenario.height;
    bind sut.step.parameters.offset = scenario.offset;
    bind sut.step.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }
}
