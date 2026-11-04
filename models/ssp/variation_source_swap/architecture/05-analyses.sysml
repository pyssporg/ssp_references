package VariationSourceSwap {
  part def step :> Analysis {
    doc /* Source variation selecting the Step FMU. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : StepSystem;

    bind sut.source.parameters.height = scenario.height;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
  }

  part def sine :> Analysis {
    doc /* Source variation selecting the Sine FMU. */
    attribute experiment : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : SineSystem;

    bind sut.source.parameters.amplitude = scenario.amplitude;
    bind sut.source.parameters.f = scenario.f;
    bind sut.source.parameters.offset = scenario.offset;
    bind sut.source.parameters.startTime = scenario.startTime;
  }
}
