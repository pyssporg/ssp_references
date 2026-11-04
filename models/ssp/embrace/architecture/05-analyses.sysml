package Embrace {
  part def baseline :> Analysis {
    doc /* EMBRACE thermal-management reference model over the baseline window. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.ECS_HW.parameters.'pipeA.L' = scenario.'pipeA.L';
    bind sut.ECS_HW.parameters.'pipeB.L' = scenario.'pipeB.L';
  }
}
