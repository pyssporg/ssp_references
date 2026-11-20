package RavsV2 {
  private import PysspCore::*;

  attribute def AdaptionFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/adaption";
    attribute implementation = "CoSimulation";
  }

  attribute def AtmosFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/atmos";
    attribute implementation = "CoSimulation";
  }

  attribute def ConsumerFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/consumer";
    attribute implementation = "CoSimulation";
  }

  attribute def EcsHwFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/ecs_hw";
    attribute implementation = "CoSimulation";
  }

  attribute def EcsSwFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/ecs_sw";
    attribute implementation = "CoSimulation";
  }

  attribute def FuelFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/fuel";
    attribute implementation = "CoSimulation";
  }

  attribute def InterfaceModelFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/interface_model";
    attribute implementation = "CoSimulation";
  }

  attribute def ValveModelFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v2/resources/valve_model";
    attribute implementation = "CoSimulation";
  }

  part def adaption :> FmuModel {
    attribute fmu_meta : AdaptionFmu;
    in port Aircraft_State : RealSignal;
    in port LHexTout : RealSignal;
    out port sWsignals : SwSignals;
  }

  part def atmos :> FmuModel {
    attribute fmu_meta : AtmosFmu;
    in port Alt : RealSignal;
    in port Ma : RealSignal;
    out port Tamb : RealSignal;
    out port Pamb : RealSignal;
  }

  part def consumer :> FmuModel {
    attribute fmu_meta : ConsumerFmu;
    in port consumerRet : FluidStateConjugate;
    out port consumerFeed : FluidState;
    in port Alt : RealSignal;
    in port Mach : RealSignal;
    in port Tamb : RealSignal;
    in port Pamb : RealSignal;
    in port heatLoad : RealSignal;
    out port inletTemp : RealSignal;
    out port outletTemp : RealSignal;
  }

  part def ecs_hw :> FmuModel {
    attribute fmu_meta : EcsHwFmu;
    in port Alt : RealSignal;
    in port Mach : RealSignal;
    in port Tamb : RealSignal;
    in port Pamb : RealSignal;
    in port consumerFeed : FluidStateConjugate;
    in port reqCoolingTemperature : RealSignal;
    out port consumerRet : FluidState;
    out port LHexTout : RealSignal;
  }

  part def ecs_sw :> FmuModel {
    attribute fmu_meta : EcsSwFmu;
    in port Input : SwSignals;
    out port TCoolingPack : RealSignal;
  }

  part def fuel :> FmuModel {
    attribute fmu_meta : FuelFmu;
    in port P_AMB : RealSignal;
    in port T_AMB : RealSignal;
    in port eng_mflow : RealSignal;
    in port Mach : RealSignal;
    in port valve_mflowA : RealSignal;
    in port valve_mflowB : RealSignal;
    in port pmh : FluidStateConjugate;
    out port valve_u : RealSignal;
    out port valve_p1 : RealSignal;
    out port valve_p2 : RealSignal;
    out port valve_p3 : RealSignal;
    out port pmhn : FluidState;
  }

  part def valve_model :> FmuModel {
    attribute fmu_meta : ValveModelFmu;
    in port parameters : ValveModelParameters;
    in port uA : RealSignal;
    in port uB : RealSignal;
    in port pP : RealSignal;
    in port pTA : RealSignal;
    in port pTB : RealSignal;
    in port pA : RealSignal;
    in port pB : RealSignal;
    in port pLin : RealSignal;
    in port pLmax : RealSignal;
    in port p_TP : RealSignal;
    in port p_PS : RealSignal;
    out port qA : RealSignal;
    out port qB : RealSignal;
    out port qP : RealSignal;
    out port qTA : RealSignal;
    out port qTB : RealSignal;
    out port pL : RealSignal;
    out port Debug : RealSignal;
  }

  part def interface_model :> FmuModel {
    attribute fmu_meta : InterfaceModelFmu;
    in port parameters : InterfaceModelParameters;
    in port 'qTA.out.y' : RealSignal;
    in port 'qTB.out.y' : RealSignal;
    in port 'u.out.y' : RealSignal;
    out port 'debug.in.y' : RealSignal;
    out port 'mflowA.in.y' : RealSignal;
    out port 'mflowB.in.y' : RealSignal;
    out port 'pLin.in.y' : RealSignal;
    out port 'pLmax.in.y' : RealSignal;
    out port 'p_P.in.y' : RealSignal;
    out port 'p_PS.in.y' : RealSignal;
    out port 'p_TP.in.y' : RealSignal;
    out port 'uA.in.y' : RealSignal;
    out port 'uB.in.y' : RealSignal;
  }

  part def valve {
    in port u : RealSignal;
    in port p1 : RealSignal;
    in port p2 : RealSignal;
    in port p3 : RealSignal;
    out port mflowA : RealSignal;
    out port mflowB : RealSignal;
    out port Debug : RealSignal;

    part valve_model : valve_model;
    part interface_model : interface_model;

    connect valve_model.pLmax to interface_model.'pLmax.in.y';
    connect valve_model.pLin to interface_model.'pLin.in.y';
    connect valve_model.pP to interface_model.'p_P.in.y';
    connect valve_model.p_PS to interface_model.'p_PS.in.y';
    connect valve_model.p_TP to interface_model.'p_TP.in.y';
    connect valve_model.uA to interface_model.'uA.in.y';
    connect valve_model.uB to interface_model.'uB.in.y';
    connect interface_model.'qTA.out.y' to valve_model.qTA;
    connect interface_model.'qTB.out.y' to valve_model.qTB;
    connect interface_model.'mflowA.in.y' to mflowA;
    connect interface_model.'mflowB.in.y' to mflowB;
    connect u to interface_model.'u.out.y';
    connect p1 to valve_model.pA;
    connect p1 to valve_model.pB;
    connect p2 to valve_model.pTA;
    connect p3 to valve_model.pTB;
    connect valve_model.Debug to Debug;
  }
}
