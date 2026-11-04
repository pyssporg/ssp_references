package VariationAttributeSet {
  part def nominal_k3 :> Analysis {
    doc /* Attribute variation selecting the k=3.0 parameter set. */
    attribute experiment_baseline : BaselineExperiment;
    attribute nominal_scenario : ScenarioChoice = ScenarioChoice::nominalK3;
    part sut : System;

    bind sut.step.parameters.height = nominal_scenario.height;
    bind sut.step.parameters.offset = nominal_scenario.offset;
    bind sut.step.parameters.startTime = nominal_scenario.startTime;
    bind sut.gain.parameters.k = nominal_scenario.k;
  }

  part def boosted_k9 :> Analysis {
    doc /* Attribute variation selecting the k=9.0 parameter set. */
    attribute experiment_baseline : BaselineExperiment;
    attribute boosted_scenario : ScenarioChoice = ScenarioChoice::boostedK9;
    part sut : System;

    bind sut.step.parameters.height = boosted_scenario.height;
    bind sut.step.parameters.offset = boosted_scenario.offset;
    bind sut.step.parameters.startTime = boosted_scenario.startTime;
    bind sut.gain.parameters.k = boosted_scenario.k;
  }
}
