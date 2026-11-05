package GainOffset {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part generator : Generator;
  }

  part def baseline :> Analysis {
    doc /* Single analytic source component; the FMU interface is authored in models/fmu/GainOffset. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
