package Scenario {
  part def SspModel;
  part def Study;

  port def ParameterInterface;

  port def ScenarioParameters :> ParameterInterface {
    attribute scenario_input : String;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute scenario_input = "Alt;L;0,0;300,5000\nMach;L;0,0;300,1.2\nheat_load;ZOH;0,50;150,4000\nWgt_On_Whl;ZOH;0,1;150,0\nAircraft_state;ZOH;0,0;150,4";
    attribute Alt_start = 0.0;
    attribute Mach_start = 0.0;
    attribute heat_load_start = 50.0;
    attribute Wgt_On_Whl_start = 1.0;
    attribute Aircraft_state_start = 0.0;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def ScenarioFmu :> FmuMetadata {
    attribute source = "models/fmu/scenario/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Scenario {
    attribute fmu_meta : ScenarioFmu;
    in port parameters : ScenarioParameters;
    out port Alt : RealSignal;
    out port Mach : RealSignal;
    out port heat_load : RealSignal;
    out port Wgt_On_Whl : RealSignal;
    out port Aircraft_state : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 10.0;
    attribute scenario_set : ScenarioSet;
    part scenario : Scenario;

    bind scenario.parameters.scenario_input = scenario_set.scenario_input;
  }

  part def baseline :> Study {
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
