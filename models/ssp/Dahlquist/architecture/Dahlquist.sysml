package Dahlquist {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def DahlquistParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def DahlquistFmu :> FmuMetadata {
    attribute source = "models/fmu/Dahlquist/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Dahlquist {
    attribute fmu_meta : DahlquistFmu;
    in port parameters : DahlquistParameters;
    out port x : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 10.0;
    part fmu : Dahlquist;
  }

  part def baseline :> Study {
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
