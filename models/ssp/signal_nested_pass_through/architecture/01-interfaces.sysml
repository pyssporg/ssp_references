package SignalNestedPassThrough {
  part def SspModel;

  part def Analysis;

  port def ParameterInterface;

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  port def AddParameters :> ParameterInterface {
    attribute k1 : Real;
    attribute k2 : Real;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
    attribute value : Real;
  }
}
