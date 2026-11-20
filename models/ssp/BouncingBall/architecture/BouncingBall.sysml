package BouncingBall {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def BouncingBallDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 3.0;
  }

  port def BouncingBallParameters :> ParameterInterface {
    attribute g : Real;
    attribute e : Real;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 3.0;
    attribute stepSize = 0.001;
  }

  attribute def BouncingBallFmu :> FmuMetadata {
    attribute source = "models/fmu/BouncingBall/fmu";
    attribute implementation = "CoSimulation";
  }

  part def BouncingBall :> FmuModel {
    attribute fmu_meta : BouncingBallFmu;
    in port parameters : BouncingBallParameters;
    out port h : RealSignal;
    out port v : RealSignal;
  }

  part def System :> SspModel {
    attribute defaults : BouncingBallDefaultExperiment;

    part fmu : BouncingBall;
  }

  part def baseline :> Analysis {
    doc /* Event-driven bouncing ball over the baseline window; no scenario. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
