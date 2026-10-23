package Stair {
  part def SspModel;
  part def Study;

  port def IntegerSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Integer;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 9.0;
    attribute stepSize = 0.2;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def StairFmu :> FmuMetadata {
    attribute source = "models/fmu/Stair/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Stair {
    attribute fmu_meta : StairFmu;
    out port counter : IntegerSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 9.0;
    part fmu : Stair;
  }

  part def baseline :> Study {
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
