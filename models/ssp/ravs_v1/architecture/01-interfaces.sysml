package RavsV1 {
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

  port def FluidState {
    attribute p : Real;
    attribute h : Real;
    attribute 'X[1]' : Real;
    attribute 'X[2]' : Real;
    attribute 'X[3]' : Real;
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
