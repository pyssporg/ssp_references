package SignalNestedAlgebraicLoop {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def SineParameters :> ParameterInterface {
    attribute amplitude : Real;
    attribute f : Real;
    attribute offset : Real;
    attribute phase : Real;
    attribute startTime : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def AddParameters :> ParameterInterface {
    attribute k1 : Real;
    attribute k2 : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }
}
