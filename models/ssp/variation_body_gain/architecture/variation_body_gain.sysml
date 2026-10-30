package VariationBodyGain {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

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
    attribute amplitude = 1.0;
    attribute f = 1.0;
    attribute offset = 0.0;
    attribute startTime = 0.5;
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

  /* One variation point: its variants are bodies, not types. */
  variation part def PathChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part oneStage {
      part gain : Gain;
      connect u to gain.u;
      connect gain.y to y;
    }

    variant part twoStages {
      part product : Product;
      part gain : Gain;
      connect u to product.u1;
      connect u to product.u2;
      connect product.y to gain.u;
      connect gain.y to y;
    }
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part source : Sine;
    part path : PathChoice;
    connect source.y to path.u;

  }

  /* Configurations: each binds the path point to one variant body. */
  part def OneStageSystem :> System {
    part :>> path = PathChoice::oneStage;
  }

  part def TwoStagesSystem :> System {
    part :>> path = PathChoice::twoStages;
  }

  part def one_stage :> Analysis {
    doc /* Body variation selecting the single-gain path. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : OneStageSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.k;
  }

  part def two_stages :> Analysis {
    doc /* Body variation selecting the product-then-gain path. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : TwoStagesSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.k;
  }
}
