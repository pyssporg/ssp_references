package SignalStepAdd {
  part def baseline :> Analysis {
    doc /* Two steps added at the root. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step_a.parameters.height = scenario.step_a_height;
    bind sut.step_a.parameters.offset = scenario.step_a_offset;
    bind sut.step_a.parameters.startTime = scenario.step_a_startTime;
    bind sut.step_b.parameters.height = scenario.step_b_height;
    bind sut.step_b.parameters.offset = scenario.step_b_offset;
    bind sut.step_b.parameters.startTime = scenario.step_b_startTime;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
  }
}
