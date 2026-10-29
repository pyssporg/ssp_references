package SignalStepAdd {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def AddParameters :> ParameterInterface {
    attribute k1 : Real;
    attribute k2 : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute step_a_height = 1.5;
    attribute step_a_offset = 0.5;
    attribute step_a_startTime = 0.25;
    attribute step_b_height = -0.5;
    attribute step_b_offset = 1.0;
    attribute step_b_startTime = 0.5;
    attribute add_k1 = 1.0;
    attribute add_k2 = 1.0;
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

  attribute def AddFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Add/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Step {
    attribute fmu_meta : StepFmu;
    in port parameters : StepParameters;
    out port y : RealSignal;
  }

  part def Add {
    attribute fmu_meta : AddFmu;
    in port parameters : AddParameters;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part step_a : Step;
    part step_b : Step;
    part add : Add;
    connect step_a.y to add.u1;
    connect step_b.y to add.u2;
  }

  part def baseline :> Analysis {
    doc /* Two steps added at the root. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step_a.parameters.height = scenario.step_a_height;
    bind sut.step_a.parameters.offset = scenario.step_a_offset;
    bind sut.step_a.parameters.startTime = scenario.step_a_startTime;
    bind sut.step_b.parameters.height = scenario.step_b_height;
    bind sut.step_b.parameters.offset = scenario.step_b_offset;
    bind sut.step_b.parameters.startTime = scenario.step_b_startTime;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
