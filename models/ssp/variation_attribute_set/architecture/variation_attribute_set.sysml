package VariationAttributeSet {
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

  attribute def NominalK3 :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 3.0;
  }

  attribute def BoostedK9 :> ParameterSet {
    attribute height = 2.0;
    attribute offset = 1.0;
    attribute startTime = 0.25;
    attribute k = 9.0;
  }

  /* One attribute variation point: both variants fix the same parameter set. */
  variation attribute def ScenarioChoice {
    variant attribute nominalK3 : NominalK3;
    variant attribute boostedK9 : BoostedK9;
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

  part def nominal_k3 :> Analysis {
    doc /* Attribute variation selecting the k=3.0 parameter set. */
    attribute experiment_baseline : BaselineExperiment;
    attribute nominal_scenario : ScenarioChoice;
    part sut : System;

    bind sut.step.parameters.height = nominal_scenario.height;
    bind sut.step.parameters.offset = nominal_scenario.offset;
    bind sut.step.parameters.startTime = nominal_scenario.startTime;
    bind sut.gain.parameters.k = nominal_scenario.k;
  }

  part def boosted_k9 :> Analysis {
    doc /* Attribute variation selecting the k=9.0 parameter set. */
    attribute experiment_baseline : BaselineExperiment;
    attribute boosted_scenario : ScenarioChoice;
    part sut : System;

    bind sut.step.parameters.height = boosted_scenario.height;
    bind sut.step.parameters.offset = boosted_scenario.offset;
    bind sut.step.parameters.startTime = boosted_scenario.startTime;
    bind sut.gain.parameters.k = boosted_scenario.k;
  }
}
