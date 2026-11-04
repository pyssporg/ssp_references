package SignalDelayDetector {
  part def baseline :> Analysis {
    doc /* Step routed through two gains and add, with a delayed detection path. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step.parameters.height = scenario.step_height;
    bind sut.step.parameters.offset = scenario.step_offset;
    bind sut.step.parameters.startTime = scenario.step_startTime;
    bind sut.gain_a.parameters.k = scenario.gain_a_k;
    bind sut.gain_b.parameters.k = scenario.gain_b_k;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
