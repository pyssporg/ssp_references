package SignalInitLoopGuard {
  private import PysspCore::*;

  part def baseline :> Analysis {
    doc /* Cyclic signal loop with a validating divider: gain (LoopGain,
         k=0.5, c=10) and div (DivideGuard, c=100) wired in a cycle. No
         topological initialization order exists; div refuses initialization
         while its input holds the default zero, because evaluating c/u
         would divide by zero. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.gain.parameters.k = scenario.gain_k;
    bind sut.gain.parameters.c = scenario.gain_c;
    bind sut.div.parameters.c = scenario.div_c;
  }
}
