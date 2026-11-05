package Embrace {
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

  port def EcsHwParameters :> ParameterInterface {
    attribute 'pipeA.L' : Real;
    attribute 'pipeB.L' : Real;
  }
}
