package BouncingBall {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def BouncingBallParameters :> ParameterInterface {
    attribute g : Real;
    attribute e : Real;
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
    attribute stopTime = 3.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def BouncingBallFmu :> FmuMetadata {
    attribute source = "models/fmu/BouncingBall/fmu";
    attribute implementation = "CoSimulation";
  }

  part def BouncingBall {
    attribute fmu_meta : BouncingBallFmu;
    in port parameters : BouncingBallParameters;
    out port h : RealSignal;
    out port v : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 3.0;
    part fmu : BouncingBall;
  }

  part def baseline :> Study {
    doc /* Event-driven bouncing ball over the baseline window; no scenario. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
