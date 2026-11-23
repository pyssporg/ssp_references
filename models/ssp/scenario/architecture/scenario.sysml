package Scenario {
  private import ScalarValues::*;
  private import PysspCore::*;

  attribute def ScenarioDefaultExperiment :> DefaultExperiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
  }

  attribute def ScenarioSet :> ParameterSet {
    attribute scenario_input = "Alt;L;0,0;300,5000\nMach;L;0,0;300,1.2\nheat_load;ZOH;0,50;150,4000\nWgt_On_Whl;ZOH;0,1;150,0\nAircraft_state;ZOH;0,0;150,4";
    attribute Alt_start = 0.0;
    attribute Mach_start = 0.0;
    attribute heat_load_start = 50.0;
    attribute Wgt_On_Whl_start = 1.0;
    attribute Aircraft_state_start = 0.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.001;
  }

  part def System :> SspModel {
    attribute defaults : ScenarioDefaultExperiment;

    attribute scenario_set : ScenarioSet;
    part scenario : Scenario;

    bind scenario.parameters.scenario_input = scenario_set.scenario_input;
  }

  part def baseline :> Analysis {
    doc /* Model-owned scenario set driving the scenario FMU outputs. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
