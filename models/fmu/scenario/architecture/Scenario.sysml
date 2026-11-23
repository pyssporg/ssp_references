package Scenario {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def ScenarioParameters :> ParameterInterface {
    attribute scenario_input : String;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def ScenarioFmu :> FmuMetadata {
    attribute source = "artifacts/build/scenario/scenario.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Scenario :> FmuModel {
    doc /* Scenario-series source: one Real output per series in scenario_input. */
    attribute fmu_meta : ScenarioFmu;
    in port parameters : ScenarioParameters;
    out port Alt : RealSignal;
    out port Mach : RealSignal;
    out port heat_load : RealSignal;
    out port Wgt_On_Whl : RealSignal;
    out port Aircraft_state : RealSignal;
  }

}
