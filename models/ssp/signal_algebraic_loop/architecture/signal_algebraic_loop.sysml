package SignalAlgebraicLoop {
  part def SspModel;
  part def Analysis;

  port def ParameterInterface;

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

  attribute def ParameterSet;

  attribute def ScenarioSet :> ParameterSet {
    attribute sine_amplitude = 1.0;
    attribute sine_f = 2.0;
    attribute sine_offset = 0.0;
    attribute sine_phase = 0.0;
    attribute sine_startTime = 0.0;
    attribute gain_k = 0.5;
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

  attribute def SineFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Sources.Sine/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def GainFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Gain/fmu";
    attribute implementation = "CoSimulation";
  }

  attribute def AddFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Add/fmu";
    attribute implementation = "CoSimulation";
  }

  part def Sine {
    attribute fmu_meta : SineFmu;
    in port parameters : SineParameters;
    out port y : RealSignal;
  }

  part def Gain {
    attribute fmu_meta : GainFmu;
    in port parameters : GainParameters;
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def Add {
    attribute fmu_meta : AddFmu;
    in port parameters : AddParameters;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    attribute pyssp_default_start_time : Real = 0.0;
    attribute pyssp_default_stop_time : Real = 1.0;
    part sine : Sine;
    part gain : Gain;
    part add : Add;
    connect sine.y to add.u1;
    connect gain.y to add.u2;
    connect add.y to gain.u;
  }

  part def baseline :> Analysis {
    doc /* Sine through gain, with the algebraic loop closed by add. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.sine.parameters.f = scenario.sine_f;
    bind sut.sine.parameters.offset = scenario.sine_offset;
    bind sut.sine.parameters.phase = scenario.sine_phase;
    bind sut.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.gain.parameters.k = scenario.gain_k;
  }
}
