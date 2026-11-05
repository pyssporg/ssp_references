package GainOffset {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

  port def GeneratorParameters :> ParameterInterface {
    attribute gain : Real = 2.0;
    attribute offset : Real = 0.5;
    attribute frequency : Real = 1.0;
  }

  port def RealSignal {
    attribute value : Real;
  }

  attribute def Experiment {
    attribute startTime : Real;
    attribute stopTime : Real;
    attribute stepSize : Real;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def GeneratorFmu :> FmuMetadata {
    attribute source = "artifacts/build/GainOffset/Generator.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Generator {
    doc /* Analytic source: y = offset + gain * sin(2 * pi * frequency * t). */
    attribute fmu_meta : GeneratorFmu;
    in port parameters : GeneratorParameters;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part generator : Generator;
  }

  part def baseline :> Analysis {
    doc /* Single analytic source component; the FMU interface is authored here. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
