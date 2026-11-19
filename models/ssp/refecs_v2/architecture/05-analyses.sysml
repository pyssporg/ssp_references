package RefecsV2 {
  private import PysspCore::*;

  part def baseline :> Analysis {
    doc /* RefECS v2 hydraulic/thermal aerospace demo over the baseline window. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.valve.interface_model.parameters.timestep = scenario.timestep;
    bind sut.valve.interface_model.parameters.pT = scenario.pT;
    bind sut.valve.interface_model.parameters.pP = scenario.pP;
    bind sut.valve.interface_model.parameters.rho = scenario.rho;
    bind sut.valve.interface_model.parameters.p_PS_const = scenario.p_PS_const;
    bind sut.valve.valve_model.parameters.d_A = scenario.d_A;
    bind sut.valve.valve_model.parameters.d_B = scenario.d_B;
    bind sut.valve.valve_model.parameters.KqMO_PABT_gain = scenario.KqMO_PABT_gain;
    bind sut.valve.valve_model.parameters.KqMI_PABT_gain = scenario.KqMI_PABT_gain;
    bind sut.valve.valve_model.parameters.KqMO_PBAT_gain = scenario.KqMO_PBAT_gain;
    bind sut.valve.valve_model.parameters.KqMI_PBAT_gain = scenario.KqMI_PBAT_gain;
  }
}
