package VariationConditionalRequires {
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

  attribute def ScenarioSet :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute amplitude = 2.0;
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

  /* Two stages: an internal part tree, not two exposed parameter ports. */
  part def CascadedGain {
    in port u : RealSignal;
    out port y : RealSignal;
    part firstStage : Gain;
    part secondStage : Gain;
    connect u to firstStage.u;
    connect firstStage.y to secondStage.u;
    connect secondStage.y to y;
  }

  variation part def SourceChoice {
    out port y : RealSignal;
    variant part stepImplementation : Step;
    variant part sineImplementation : Sine;
  }

  variation part def GainChoice {
    in port u : RealSignal;
    out port y : RealSignal;
    variant part singleStage : Gain;
    variant part twoStages : CascadedGain;
  }

  /* A condition over two variation points. The adapter captures and evaluates it;
   * build.py asks the adapter and rejects the illegal branch. */
  constraint def SineRequiresSingleStage {
    in chosenSource : SourceChoice;
    in chosenGain : GainChoice;
    chosenSource == SourceChoice::sineImplementation implies
      chosenGain == GainChoice::singleStage
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : SourceChoice;
    part gain : GainChoice;
    connect source.y to gain.u;

    constraint requiresSingleStage : SineRequiresSingleStage {
      in chosenSource = source;
      in chosenGain = gain;
    }
    assert requiresSingleStage;
  }

  part def step_single :> Analysis {
    doc /* Legal: step source with a single gain stage. */
    attribute pyssp_selection = "source=stepImplementation;gain=singleStage";
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def step_two :> Analysis {
    doc /* Legal: step source with two gain stages. */
    attribute pyssp_selection = "source=stepImplementation;gain=twoStages";
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.firstStage.parameters.k = scenario.k;
    bind sut.gain.secondStage.parameters.k = scenario.k;
  }

  part def sine_single :> Analysis {
    doc /* Legal: the sine source requires the single gain stage. */
    attribute pyssp_selection = "source=sineImplementation;gain=singleStage";
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def sine_two :> Analysis {
    doc /* Illegal: the constraint rejects sine with two gain stages. */
    attribute pyssp_selection = "source=sineImplementation;gain=twoStages";
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.firstStage.parameters.k = scenario.k;
    bind sut.gain.secondStage.parameters.k = scenario.k;
  }
}
