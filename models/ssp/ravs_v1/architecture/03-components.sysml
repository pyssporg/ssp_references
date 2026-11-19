package RavsV1 {
  private import PysspCore::*;

  attribute def EcsHwFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/0001_ECS_HW";
    attribute implementation = "CoSimulation";
  }

  attribute def EcsSwFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/0002_ECS_SW";
    attribute implementation = "CoSimulation";
  }

  attribute def ConsumerFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/0003_Consumer";
    attribute implementation = "CoSimulation";
  }

  attribute def AtmosFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/0004_Atmos";
    attribute implementation = "CoSimulation";
  }

  attribute def AdaptionUnitFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/0005_AdaptionUnit";
    attribute implementation = "CoSimulation";
  }

  attribute def BcFmu :> FmuMetadata {
    attribute source = "models/ssp/ravs_v1/resources/BC";
    attribute implementation = "CoSimulation";
  }

  part def ECS_HW {
    attribute fmu_meta : EcsHwFmu;
    in port parameters : EcsHwParameters;
    in port Alt : RealSignal;
    in port Mach : RealSignal;
    in port Tamb : RealSignal;
    in port Pamb : RealSignal;
    in port consumerFeed : FluidState;
    in port consumerRet : FluidState;
    in port reqCoolingTemperature : RealSignal;
    out port 'consumerFeed.m' : RealSignal;
    out port 'consumerFeed.hn' : RealSignal;
    out port 'consumerRet.m' : RealSignal;
    out port 'consumerRet.hn' : RealSignal;
    out port LHexTout : RealSignal;
  }

  part def ECS_SW {
    attribute fmu_meta : EcsSwFmu;
    in port Input : SwSignals;
    out port TCoolingPack : RealSignal;
  }

  part def Consumer {
    attribute fmu_meta : ConsumerFmu;
    in port 'consumerRet.m' : RealSignal;
    in port 'consumerRet.hn' : RealSignal;
    in port 'consumerFeed.m' : RealSignal;
    in port 'consumerFeed.hn' : RealSignal;
    in port Alt : RealSignal;
    in port Mach : RealSignal;
    in port Tamb : RealSignal;
    in port Pamb : RealSignal;
    in port heatLoad : RealSignal;
    out port consumerRet : FluidState;
    out port consumerFeed : FluidState;
    out port inletTemp : RealSignal;
    out port outletTemp : RealSignal;
  }

  part def Atmos {
    attribute fmu_meta : AtmosFmu;
    in port Alt : RealSignal;
    in port Ma : RealSignal;
    out port Tamb : RealSignal;
    out port Pamb : RealSignal;
  }

  part def AdaptionUnit {
    attribute fmu_meta : AdaptionUnitFmu;
    in port Aircraft_State : RealSignal;
    in port LHexTout : RealSignal;
    out port sWsignals : SwSignals;
  }

  part def BC {
    attribute fmu_meta : BcFmu;
    out port Alt : RealSignal;
    out port Mach : RealSignal;
    out port heatLoad : RealSignal;
    out port WGT_ON_WHL : RealSignal;
    out port Aircraft_state : RealSignal;
  }
}
