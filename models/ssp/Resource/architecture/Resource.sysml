package Resource {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def ResourceDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  port def IntegerSignal {
    attribute value : Integer;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
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
    attribute defaults : ResourceDefaultExperiment;

    part fmu : Resource;
  }

  part def baseline :> Analysis {
    doc /* Constant integer output loaded from the FMU's bundled resource file. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
