package SignalSineGainAdd {
  part def baseline :> Analysis {
    doc /* Sine through a gain plus a step, added at the root. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.sine.parameters.f = scenario.sine_f;
    bind sut.sine.parameters.offset = scenario.sine_offset;
    bind sut.sine.parameters.phase = scenario.sine_phase;
    bind sut.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.step.parameters.height = scenario.step_height;
    bind sut.step.parameters.offset = scenario.step_offset;
    bind sut.step.parameters.startTime = scenario.step_startTime;
    bind sut.gain.parameters.k = scenario.gain_k;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
