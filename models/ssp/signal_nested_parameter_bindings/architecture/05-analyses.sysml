package SignalNestedParameterBindings {
  part def baseline :> Analysis {
    doc /* Nested inline parameter sets plus a root external mapping. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step.parameters.height = scenario.step_height;
    bind sut.step.parameters.offset = scenario.step_offset;
    bind sut.step.parameters.startTime = scenario.step_startTime;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
    bind sut.inner.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.inner.sine.parameters.f = scenario.sine_f;
    bind sut.inner.sine.parameters.offset = scenario.sine_offset;
    bind sut.inner.sine.parameters.phase = scenario.sine_phase;
    bind sut.inner.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.inner.gain.parameters.k = scenario.gain_k;
  }
}
