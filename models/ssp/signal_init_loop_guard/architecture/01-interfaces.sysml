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
    attribute value : Real;
  }
}
