package SignalInitLoop {
  private import PysspCore::*;

  part def baseline :> Analysis {
    doc /* Signal loop requiring iterative initialization: gain_a (LoopGain,
         k=0.5, c=10) and gain_b (LoopGain, k=0.5, c=0) wired in a cycle.
         No topological initialization order exists; the consistent start
         values are the loop's fixed point (y_a = 40/3, y_b = 20/3). */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.gain_a.parameters.k = scenario.gain_a_k;
    bind sut.gain_a.parameters.c = scenario.gain_a_c;
    bind sut.gain_b.parameters.k = scenario.gain_b_k;
    bind sut.gain_b.parameters.c = scenario.gain_b_c;
  }
}
