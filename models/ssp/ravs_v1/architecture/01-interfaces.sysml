package RavsV1 {
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

  port def FluidStateConjugate {
    in attribute p : Real;
    in attribute h : Real;
    in attribute X : Real[3];
    out attribute m : Real;
    out attribute hn : Real;
  }

  port def SwSignals {
    attribute TLiquid : Real;
    attribute Aircraft_State : Integer;
  }

  port def EcsHwParameters :> ParameterInterface {
    attribute 'pipeA.L' : Real;
    attribute 'pipeB.L' : Real;
  }
}
