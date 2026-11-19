package RefecsV2 {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }

  port def IntegerSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Integer;
  }

  port def InterfaceModelParameters :> ParameterInterface {
    attribute timestep : Real;
    attribute pT : Real;
    attribute pP : Real;
    attribute rho : Real;
    attribute p_PS_const : Real;
  }

  port def ValveModelParameters :> ParameterInterface {
    attribute d_A : Real;
    attribute d_B : Real;
    attribute KqMO_PABT_gain : Real;
    attribute KqMI_PABT_gain : Real;
    attribute KqMO_PBAT_gain : Real;
    attribute KqMI_PBAT_gain : Real;
  }
}
