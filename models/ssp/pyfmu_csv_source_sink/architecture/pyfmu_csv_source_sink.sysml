package PyfmuCsvSourceSink {
  part def SspModel;

  port def ParameterInterface;
  attribute def ParameterSet;

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

  attribute def FmuMetadata {
    attribute source : String;
    attribute resource_name : String;
    attribute implementation : String;
  }

  attribute def CsvSourceFmu :> FmuMetadata {
    attribute resource_name = "CsvSource.fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute resource_name = "Gain.fmu";
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
    part source : CsvSource;
    part sink : Gain;
    connect source.y to sink.u;
  }
}
