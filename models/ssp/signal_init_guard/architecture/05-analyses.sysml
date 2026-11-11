package SignalInitGuard {
  private import PysspCore::*;

  part def baseline :> Analysis {
    doc /* Signal chain with a validating guard: source (Sine) -> guard
         (InitGuard) -> add (Add). The guard fails initialization with a
         hard assert when its connected input still holds the default zero,
         turning the silent independent-initialization failure into a crash. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.amplitude = scenario.sine_amplitude;
    bind sut.source.parameters.f = scenario.sine_f;
    bind sut.source.parameters.offset = scenario.sine_offset;
    bind sut.source.parameters.phase = scenario.sine_phase;
    bind sut.source.parameters.startTime = scenario.sine_startTime;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
