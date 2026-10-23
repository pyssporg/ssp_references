package SignalNestedAlgebraicLoop {
  part def SspModel;
  part def Study;

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
    attribute sine_amplitude = 0.5;
    attribute sine_f = 2.0;
    attribute sine_offset = 1.0;
    attribute sine_phase = 0.0;
    attribute sine_startTime = 0.0;
    attribute gain_outer_k = 0.25;
    attribute gain_inner_k = 0.5;
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
    part gain_outer : Gain;
    part gain_inner : Gain;
    part add_outer : Add;
    part add_inner : Add;
    connect sine.y to add_outer.u1;
    connect add_inner.y to add_outer.u2;
    connect add_outer.y to gain_outer.u;
    connect gain_outer.y to add_inner.u1;
    connect gain_inner.y to add_inner.u2;
    connect add_inner.y to gain_inner.u;
  }

  part def baseline :> Study {
    doc /* Nested systems closing an algebraic loop around add and gain. */
    attribute experiment_baseline : BaselineExperiment;
    attribute scenario : ScenarioSet;
    part sut : System;

    bind sut.sine.parameters.amplitude = scenario.sine_amplitude;
    bind sut.sine.parameters.f = scenario.sine_f;
    bind sut.sine.parameters.offset = scenario.sine_offset;
    bind sut.sine.parameters.phase = scenario.sine_phase;
    bind sut.sine.parameters.startTime = scenario.sine_startTime;
    bind sut.gain_outer.parameters.k = scenario.gain_outer_k;
    bind sut.gain_inner.parameters.k = scenario.gain_inner_k;
  }
}
