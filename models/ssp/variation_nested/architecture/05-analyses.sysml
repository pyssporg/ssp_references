package VariationNested {
  part def direct :> Analysis {
    doc /* Outer variation selecting the single-gain path. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : DirectSystem;

    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.gainK;
  }

  part def nested_gain :> Analysis {
    doc /* Nested path with a Gain stage. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : NestedGainSystem;

    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.output_gain.parameters.k = scenario.gainK;
    bind sut.path.inner_stage.gain.parameters.k = scenario.stageK;
  }
}
