package GainOffset {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def GainOffsetDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def System :> SspModel {
    attribute defaults : GainOffsetDefaultExperiment;

    part generator : Generator;
  }

  part def baseline :> Analysis {
    doc /* Single analytic source component; the FMU interface is authored in models/fmu/GainOffset. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
