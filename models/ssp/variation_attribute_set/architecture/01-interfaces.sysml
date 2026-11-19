package VariationAttributeSet {
  private import ScalarValues::*;
  private import PysspCore::*;
  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute value : Real;
  }
}
