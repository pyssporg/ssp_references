package Resource {
  part def SspModel;
  part def Analysis;

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
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def ResourceFmu :> FmuMetadata {
    attribute source = "models/fmu/Resource/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Resource {
    attribute fmu_meta : ResourceFmu;
    out port y : IntegerSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part fmu : Resource;
  }

  part def baseline :> Analysis {
    doc /* Constant integer output loaded from the FMU's bundled resource file. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
