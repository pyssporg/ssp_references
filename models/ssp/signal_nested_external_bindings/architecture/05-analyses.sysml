package SignalNestedExternalBindings {
  part def baseline :> Analysis {
    doc /* Nested system boundary wired through an external binding. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step.parameters.height = scenario.step_height;
    bind sut.step.parameters.offset = scenario.step_offset;
    bind sut.step.parameters.startTime = scenario.step_startTime;
    bind sut.inner.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.inner.sine.parameters.f = scenario.sine_f;
    bind sut.inner.sine.parameters.offset = scenario.sine_offset;
  }
}
