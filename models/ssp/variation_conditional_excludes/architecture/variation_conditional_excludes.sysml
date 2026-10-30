package VariationConditionalExcludes {
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
    attribute amplitude = 2.0;
    attribute f = 1.0;
    attribute k = 3.0;
  }

  attribute def HighGainScenario :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute amplitude = 2.0;
    attribute f = 1.0;
    attribute k = 9.0;
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
    in port parameters : GainParameters;
    out port y : RealSignal;
  }

  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation attribute def ScenarioChoice {
    variant attribute baseline : BaselineScenario;
    variant attribute highGain : HighGainScenario;
  }

  /* A condition that crosses from a structural point to an attribute point.
   * The adapter captures and evaluates it; build.py asks the adapter. */
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
    part gain : Gain;
    connect source.y to gain.u;
  }

  part def step_baseline :> Analysis {
    doc /* Legal: step source with the baseline scenario. */
    attribute pyssp_selection = "source=stepImplementation;step_baseline_scenario=baseline";
    attribute experiment : BaselineExperiment;
    attribute step_baseline_scenario : ScenarioChoice;
    part sut : System;

    bind sut.source.parameters.height = step_baseline_scenario.height;
    bind sut.source.parameters.offset = step_baseline_scenario.offset;
    bind sut.source.parameters.startTime = step_baseline_scenario.startTime;
    bind sut.gain.parameters.k = step_baseline_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = step_baseline_scenario;
    }
    assert excludesHighGain;
  }

  part def step_high :> Analysis {
    doc /* Legal: step source with the high-gain scenario. */
    attribute pyssp_selection = "source=stepImplementation;step_high_scenario=highGain";
    attribute experiment : BaselineExperiment;
    attribute step_high_scenario : ScenarioChoice;
    part sut : System;

    bind sut.source.parameters.height = step_high_scenario.height;
    bind sut.source.parameters.offset = step_high_scenario.offset;
    bind sut.source.parameters.startTime = step_high_scenario.startTime;
    bind sut.gain.parameters.k = step_high_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = step_high_scenario;
    }
    assert excludesHighGain;
  }

  part def sine_baseline :> Analysis {
    doc /* Legal: sine source with the baseline scenario. */
    attribute pyssp_selection = "source=sineImplementation;sine_baseline_scenario=baseline";
    attribute experiment : BaselineExperiment;
    attribute sine_baseline_scenario : ScenarioChoice;
    part sut : System;

    bind sut.source.parameters.amplitude = sine_baseline_scenario.amplitude;
    bind sut.source.parameters.f = sine_baseline_scenario.f;
    bind sut.source.parameters.offset = sine_baseline_scenario.offset;
    bind sut.source.parameters.startTime = sine_baseline_scenario.startTime;
    bind sut.gain.parameters.k = sine_baseline_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = sine_baseline_scenario;
    }
    assert excludesHighGain;
  }

  part def sine_high :> Analysis {
    doc /* Illegal: the constraint rejects sine with the high-gain scenario. */
    attribute pyssp_selection = "source=sineImplementation;sine_high_scenario=highGain";
    attribute experiment : BaselineExperiment;
    attribute sine_high_scenario : ScenarioChoice;
    part sut : System;

    bind sut.source.parameters.amplitude = sine_high_scenario.amplitude;
    bind sut.source.parameters.f = sine_high_scenario.f;
    bind sut.source.parameters.offset = sine_high_scenario.offset;
    bind sut.source.parameters.startTime = sine_high_scenario.startTime;
    bind sut.gain.parameters.k = sine_high_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = sine_high_scenario;
    }
    assert excludesHighGain;
  }
}
