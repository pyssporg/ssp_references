package SignalNestedPassThrough {
  part def baseline :> Analysis {
    doc /* Nested pass-through system feeding the add block. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.step.parameters.height = scenario.step_height;
    bind sut.step.parameters.offset = scenario.step_offset;
    bind sut.step.parameters.startTime = scenario.step_startTime;
    bind sut.add.parameters.k1 = scenario.add_k1;
    bind sut.add.parameters.k2 = scenario.add_k2;
    bind sut.inner.gain.parameters.k = scenario.inner_gain_k;
  }
}
