package SignalAlgebraicLoop {
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute sine_amplitude = 1.0;
    attribute sine_f = 2.0;
    attribute sine_offset = 0.0;
    attribute sine_phase = 0.0;
    attribute sine_startTime = 0.0;
    attribute gain_k = 0.5;
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
