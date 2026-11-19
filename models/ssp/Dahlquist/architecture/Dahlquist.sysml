package Dahlquist {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def DahlquistDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
  }

  port def DahlquistParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.001;
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
    attribute defaults : DahlquistDefaultExperiment;

    part fmu : Dahlquist;
  }

  part def baseline :> Analysis {
    doc /* Dahlquist test equation over the baseline window; no scenario. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
