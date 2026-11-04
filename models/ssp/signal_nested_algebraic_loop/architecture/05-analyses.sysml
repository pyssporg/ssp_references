package SignalNestedAlgebraicLoop {
  part def baseline :> Analysis {
    doc /* Nested systems closing an algebraic loop around add and gain. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.sine.parameters.f = scenario.sine_f;
    bind sut.sine.parameters.offset = scenario.sine_offset;
    bind sut.sine.parameters.phase = scenario.sine_phase;
    bind sut.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.gain_outer.parameters.k = scenario.gain_outer_k;
    bind sut.gain_inner.parameters.k = scenario.gain_inner_k;
  }
}
