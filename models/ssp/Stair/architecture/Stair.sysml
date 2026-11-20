package Stair {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def StairDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 9.0;
  }

  port def IntegerSignal {
    attribute value : Integer;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 9.0;
    attribute stepSize = 0.2;
  }

  attribute def StairFmu :> FmuMetadata {
    attribute source = "models/fmu/Stair/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Stair :> FmuModel {
    attribute fmu_meta : StairFmu;
    out port counter : IntegerSignal;
  }

  part def System :> SspModel {
    attribute defaults : StairDefaultExperiment;

    part fmu : Stair;
  }

  part def baseline :> Analysis {
    doc /* Integer counter driven by time events over the baseline window. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
