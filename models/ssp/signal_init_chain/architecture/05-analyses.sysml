package SignalInitChain {
  private import PysspCore::*;

  part def baseline :> Analysis {
    doc /* Signal chain: source (Sine) -> gain (Gain) -> add (Add).
         A strict chain where every downstream FMU has a connected input, exposing
         what each component commits at the start-time frontier during
         initialization. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.source.parameters.amplitude = scenario.sine_amplitude;
    bind sut.source.parameters.f = scenario.sine_f;
    bind sut.source.parameters.offset = scenario.sine_offset;
    bind sut.source.parameters.phase = scenario.sine_phase;
    bind sut.source.parameters.startTime = scenario.sine_startTime;
    bind sut.gain.parameters.k = scenario.gain_k;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
