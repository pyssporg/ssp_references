package SignalAlgebraicLoop {
  part def baseline :> Analysis {
    doc /* Sine through gain, with the algebraic loop closed by add. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.sine.parameters.f = scenario.sine_f;
    bind sut.sine.parameters.offset = scenario.sine_offset;
    bind sut.sine.parameters.phase = scenario.sine_phase;
    bind sut.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.gain.parameters.k = scenario.gain_k;
  }
}
