package SignalDelayDetector {
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute step_height = 1.0;
    attribute step_offset = 0.5;
    attribute step_startTime = 0.25;
    attribute gain_a_k = 1.0;
    attribute gain_b_k = 1.0;
    attribute add_k1 = 1.0;
    attribute add_k2 = -1.0;
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
}
