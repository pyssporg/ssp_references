package VariationBodyGain {
  part def one_stage :> Analysis {
    doc /* Body variation selecting the single-gain path. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : OneStageSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.k;
  }

  part def two_stages :> Analysis {
    doc /* Body variation selecting the product-then-gain path. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : TwoStagesSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.path.gain.parameters.k = scenario.k;
  }
}
