package SignalInitLoopGuard {
  private import ScalarValues::*;
  private import PysspCore::*;

  port def LoopGainParameters :> ParameterInterface {
    attribute k : Real;
    attribute c : Real;
  }

  port def DivideGuardParameters :> ParameterInterface {
    attribute c : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }
}
