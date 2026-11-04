package VariationConditionalRequires {
  part def step_single :> Analysis {
    doc /* Legal: step source with a single gain stage. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : StepSingleSystem;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def step_two :> Analysis {
    doc /* Legal: step source with two gain stages. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : StepTwoSystem;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.firstStage.parameters.k = scenario.k;
    bind sut.gain.secondStage.parameters.k = scenario.k;
  }

  part def sine_single :> Analysis {
    doc /* Legal: the sine source requires the single gain stage. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : SineSingleSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.parameters.k = scenario.k;
  }

  part def sine_two :> Analysis {
    doc /* Illegal: the constraint rejects sine with two gain stages. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : SineTwoSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
    bind sut.gain.firstStage.parameters.k = scenario.k;
    bind sut.gain.secondStage.parameters.k = scenario.k;
  }
}
