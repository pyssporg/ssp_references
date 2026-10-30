package VariationNested {
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

  attribute def ProductFmu :> FmuMetadata {
    attribute source = "models/fmu/Modelica.Blocks.Math.Product/fmu";
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

  part def Product {
    attribute fmu_meta : ProductFmu;
    in port u1 : RealSignal;
    in port u2 : RealSignal;
    out port y : RealSignal;
  }

  /* Inner stage candidates: one or two gains behind one interface. */
  part def GainStage {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;
    part gain : Gain;
    connect stage_in to gain.u;
    connect gain.y to stage_out;
  }

  part def SecondStage {
    in port stage_in : RealSignal;
    out port stage_out : RealSignal;
    part gain2 : Gain;
    connect stage_in to gain2.u;
    connect gain2.y to stage_out;
  }

  part def DirectPath {
    in port u : RealSignal;
    out port y : RealSignal;
    part gain : Gain;
    connect u to gain.u;
    connect gain.y to y;
  }

  /* The inner variation usage exists only inside the nested outer body. */
  part def NestedPath {
    in port u : RealSignal;
    out port y : RealSignal;
    variation part inner_stage : StageChoice;
    part output_gain : Gain;
    connect u to inner_stage.stage_in;
    connect inner_stage.stage_out to output_gain.u;
    connect output_gain.y to y;
  }
}
