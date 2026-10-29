package VariationNested {
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
    attribute offset = 0.0;
    attribute startTime = 0.5;
    attribute gainK = 3.0;
    attribute stageK = 5.0;
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

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def ProductFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Product/fmu";
    attribute implementation = "CoSimulation";
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

  part def Product {
    attribute fmu_meta : ProductFmu;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }

  /* Inner stage candidates: one or two gains behind one interface. */
  part def GainStage {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;
    part gain : Gain;
    connect stage_in to gain.u;
    connect gain.y to stage_out;
  }

  part def SecondStage {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;
    part gain2 : Gain;
    connect stage_in to gain2.u;
    connect gain2.y to stage_out;
  }

  variation part def StageChoice {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;

    variant part gainStage : GainStage;
    variant part secondStage : SecondStage;
  }

  part def DirectPath {
    in port u : RealSignal;
    out port y : RealSignal;
    part gain : Gain;
    connect u to gain.u;
    connect gain.y to y;
  }

  /* The inner variation usage exists only inside the nested outer body. */
  part def NestedPath {
    in port u : RealSignal;
    out port y : RealSignal;
    variation part inner_stage : StageChoice;
    part output_gain : Gain;
    connect u to inner_stage.stage_in;
    connect inner_stage.stage_out to output_gain.u;
    connect output_gain.y to y;
  }

  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part directPath : DirectPath;
    variant part nestedPath : NestedPath;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Sine;
    part path : PathChoice;

    connect source.y to path.u;

  }

  part def direct :> Study {
    doc /* Outer variation selecting the single-gain path. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.gainK;
  }

  part def nested_gain :> Study {
    doc /* Nested path with a Gain stage. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.output_gain.parameters.k = scenario.gainK;
    bind sut.path.inner_stage.gain.parameters.k = scenario.stageK;
  }

}
