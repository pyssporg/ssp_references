package RavsV2 {
  private import PysspCore::*;

  attribute def ScenarioSet :> ParameterSet {
    attribute timestep = 0.001;
    attribute pT = 1.0;
    attribute pP = 1.0;
    attribute rho = 1000.0;
    attribute p_PS_const = 35.0;
    attribute d_A = 2.0;
    attribute d_B = 2.0;
    attribute KqMO_PABT_gain = 1.0;
    attribute KqMI_PABT_gain = 1.0;
    attribute KqMO_PBAT_gain = 1.0;
    attribute KqMI_PBAT_gain = 1.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 10.0;
    attribute stepSize = 0.0333;
  }
}
