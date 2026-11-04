package VariationConditionalExcludes {
  part def step_baseline :> Analysis {
    doc /* Legal: step source with the baseline scenario. */
    attribute experiment : BaselineExperiment;
    attribute step_baseline_scenario : ScenarioChoice = ScenarioChoice::baseline;
    part sut : StepSystem;

    bind sut.source.parameters.height = step_baseline_scenario.height;
    bind sut.source.parameters.offset = step_baseline_scenario.offset;
    bind sut.source.parameters.startTime = step_baseline_scenario.startTime;
    bind sut.gain.parameters.k = step_baseline_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = step_baseline_scenario;
    }
    assert excludesHighGain;
  }

  part def step_high :> Analysis {
    doc /* Legal: step source with the high-gain scenario. */
    attribute experiment : BaselineExperiment;
    attribute step_high_scenario : ScenarioChoice = ScenarioChoice::highGain;
    part sut : StepSystem;

    bind sut.source.parameters.height = step_high_scenario.height;
    bind sut.source.parameters.offset = step_high_scenario.offset;
    bind sut.source.parameters.startTime = step_high_scenario.startTime;
    bind sut.gain.parameters.k = step_high_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = step_high_scenario;
    }
    assert excludesHighGain;
  }

  part def sine_baseline :> Analysis {
    doc /* Legal: sine source with the baseline scenario. */
    attribute experiment : BaselineExperiment;
    attribute sine_baseline_scenario : ScenarioChoice = ScenarioChoice::baseline;
    part sut : SineSystem;

    bind sut.source.parameters.amplitude = sine_baseline_scenario.amplitude;
    bind sut.source.parameters.f = sine_baseline_scenario.f;
    bind sut.source.parameters.offset = sine_baseline_scenario.offset;
    bind sut.source.parameters.startTime = sine_baseline_scenario.startTime;
    bind sut.gain.parameters.k = sine_baseline_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = sine_baseline_scenario;
    }
    assert excludesHighGain;
  }

  part def sine_high :> Analysis {
    doc /* Illegal: the constraint rejects sine with the high-gain scenario. */
    attribute experiment : BaselineExperiment;
    attribute sine_high_scenario : ScenarioChoice = ScenarioChoice::highGain;
    part sut : SineSystem;

    bind sut.source.parameters.amplitude = sine_high_scenario.amplitude;
    bind sut.source.parameters.f = sine_high_scenario.f;
    bind sut.source.parameters.offset = sine_high_scenario.offset;
    bind sut.source.parameters.startTime = sine_high_scenario.startTime;
    bind sut.gain.parameters.k = sine_high_scenario.k;

    constraint excludesHighGain : SineExcludesHighGain {
      in chosenSource = sut.source;
      in chosenScenario = sine_high_scenario;
    }
    assert excludesHighGain;
  }
}
