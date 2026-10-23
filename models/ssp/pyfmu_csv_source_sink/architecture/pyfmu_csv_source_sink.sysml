package PyfmuCsvSourceSink {
  part def SspModel;
  part def Study;

  port def ParameterInterface;
  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute k = 1.0;
  }

  port def CsvSourceParameters :> ParameterInterface {
    attribute csv_path : String;
  }

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def RealSignal {
    attribute pyssp_flat_connector : Boolean = true;
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

  attribute def CsvSourceFmu :> FmuMetadata {
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  part def CsvSource {
    attribute fmu_meta : CsvSourceFmu;
    in port parameters : CsvSourceParameters;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port parameters : GainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    attribute scenario : ScenarioSet;
    part source : CsvSource;
    part sink : Gain;
    connect source.y to sink.u;
    bind sink.parameters.k = scenario.k;
  }

  part def baseline :> Study {
    doc /* CSV source driving a gain sink; the System owns the scenario. */
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}
