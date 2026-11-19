package RavsV2 {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def RealSignal {
    attribute value : Real;
  }

  port def FluidState {
    out attribute p : Real;
    out attribute h : Real;
    out attribute X : Real[3];
    in attribute m : Real;
    in attribute hn : Real;
  }

  port def SwSignals {
    attribute TLiquid : Real;
    attribute Aircraft_State : Integer;
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
