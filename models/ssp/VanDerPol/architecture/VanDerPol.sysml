package VanDerPol {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def VanDerPolParameters :> ParameterInterface {
    attribute mu : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def ParameterSet;

  attribute def FastScenario :> ParameterSet {
    attribute mu = 2.0;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 20.0;
    attribute stepSize = 0.001;
  }

  attribute def FastExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def VanDerPolFmu :> FmuMetadata {
    attribute source = "models/fmu/VanDerPol/fmu";
    attribute implementation = "CoSimulation";
  }

  part def VanDerPol {
    attribute fmu_meta : VanDerPolFmu;
    in port parameters : VanDerPolParameters;
    out port x0 : RealSignal;
    out port x1 : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 20.0;
    part fmu : VanDerPol;
  }

  part def baseline :> Study {
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }

  part def fast :> Study {
    attribute experiment_fast : FastExperiment;
    attribute scenario : FastScenario;
    part sut : System;

    bind sut.fmu.parameters.mu = scenario.mu;
  }
}
