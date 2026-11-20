package RecoveredFromSSD {
  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  port def ParameterInterface;

  port def Port_1 {
    attribute value : Real;
  }

  port def StepParameters :> ParameterInterface {
    attribute height : Real;
    attribute offset : Real;
    attribute startTime : Real;
  }

  attribute def FmuMetadata {
    attribute implementation : String;
    attribute source : String;
  }

  attribute def GainFmuMetadata :> FmuMetadata {
    attribute implementation : String = "CoSimulation";
  }

  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute height : Real = 2.0;
    attribute k : Real = 3.0;
    attribute offset : Real = 1.0;
    attribute startTime : Real = 0.25;
  }

  attribute def StepFmuMetadata :> FmuMetadata {
    attribute implementation : String = "CoSimulation";
  }

  attribute def SystemDefaults :> DefaultExperiment {
    attribute startTime : Real = 0.0;
    attribute stopTime : Real = 1.0;
  }

  part def FmuModel;

  part def Gain :> FmuModel {
    attribute fmu_meta : GainFmuMetadata;
    in port parameters : GainParameters;
    in port u : Port_1;
    out port y : Port_1;
  }

  part def Step :> FmuModel {
    attribute fmu_meta : StepFmuMetadata;
    in port parameters : StepParameters;
    out port y : Port_1;
  }

  part def System {
    attribute ScenarioSet : ScenarioSet;
    attribute defaults : SystemDefaults;
    part gain : Gain;
    part step : Step;
    connect step.y to gain.u;
    bind gain.parameters.k = ScenarioSet.k;
    bind step.parameters.height = ScenarioSet.height;
    bind step.parameters.offset = ScenarioSet.offset;
    bind step.parameters.startTime = ScenarioSet.startTime;
  }
}
